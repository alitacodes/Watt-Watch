import cv2
import time
import os
import sys
import json
import threading
import requests
import torch
from ultralytics import YOLO
import pymysql
from dotenv import load_dotenv

from twilio.rest import Client

automation = True

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT", 25060))
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME")
TW_SID = os.getenv("TW_SID")
TW_AUTH_TOKEN = os.getenv("TW_AUTH_TOKEN")
TW_FROM_NUMBER = os.getenv("TW_FROM_NUMBER")
TW_TO_NUMBER = os.getenv("TW_TO_NUMBER")
ESP_SERVER = os.getenv("ESP_SERVER", "http://192.168.0.115:5000")

def send_sms(body):
    account_sid = TW_SID
    auth_token = TW_AUTH_TOKEN
    client = Client(account_sid, auth_token)
    try:
        message = client.messages.create(
            from_ = TW_FROM_NUMBER,
            to    = TW_TO_NUMBER,
            body  = body
        )
        print(f"[SMS] Sent SID: {message.sid}")
    except Exception as e:
        print(f"[SMS ERROR] Failed to send SMS: {e}")

def turn_off_appliance(appliance):
    """Send GET to IoT server to turn off appliance, then update esp.json."""
    # Split key e.g. "1e0" → room="1", appl="e0"
    room = appliance.split('e')[0]
    appl = 'e' + appliance.split('e')[1]
    url  = f"{ESP_SERVER}/{room}/{appl}/0"
    try:
        resp = requests.get(url, timeout=5)
        print(f"[AUTO] Sent OFF → {url}  status={resp.status_code}  body={resp.text}")
    except Exception as e:
        print(f"[AUTO ERROR] Failed to reach IoT server: {e}")
        return

    # Update local esp.json so the loop picks up the change immediately
    try:
        with open(ESP_JSON) as f:
            data = json.load(f)
        data[appliance] = 0
        with open(ESP_JSON, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"[AUTO] esp.json updated: {appliance} → OFF")
    except Exception as e:
        print(f"[AUTO WARN] Could not update esp.json: {e}")



def get_db_connection():
    """
    Creates and returns a secure connection to the DigitalOcean MySQL database.
    """
    try:
        connection = pymysql.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASS,
            database=DB_NAME,
            cursorclass=pymysql.cursors.DictCursor,
            # DigitalOcean requires SSL. Passing an empty/basic config forces SSL mode.
            ssl={
                "reject_hostname": False
            }
        )
        return connection
    except pymysql.MySQLError as e:
        logging.error(f"Error connecting to MySQL Database: {e}")
        raise
con = get_db_connection()
# ---------------------------------------------------------------------------
# ESP JSON PATH — live-reloaded every loop iteration
# ---------------------------------------------------------------------------
ESP_JSON = os.path.join(os.path.dirname(__file__), "esp.json")

def load_esp_state():
    """Read esp.json from disk. Falls back to all-off on error."""
    try:
        with open(ESP_JSON) as f:
            return json.load(f)
    except Exception as e:
        print(f"[WARN] Could not read esp.json: {e}")
        return {}

def check_appl(esp_state, room_id):
    """Return appliances belonging to this room."""
    return {k: v for k, v in esp_state.items() if k.split('e')[0] == str(room_id)}

def get_energy_loss(app_id: int, duration_min: float) -> float | None:
    """Query wattage for app_id, compute and return energy loss in Wh. Prints result."""
    try:
        with con.cursor() as cursor:
            cursor.execute("SELECT wattage FROM appliance WHERE id = %s", (app_id,))
            row = cursor.fetchone()
        if not row:
            print(f"[DB WARN] No appliance found for id={app_id}")
            return None
        wattage  = row["wattage"]               # W
        loss_wh  = wattage * (duration_min / 60) # Wh
        print(f"[ENERGY LOSS]  app_id={app_id}  wattage={wattage}W  "
              f"duration={duration_min:.2f}min  loss={loss_wh:.4f}Wh")
        return loss_wh
    except Exception as e:
        print(f"[DB ERROR] get_energy_loss: {e}")
        return None

# ---------------------------------------------------------------------------
# ZONE MAPPING — built from DB at startup
# ---------------------------------------------------------------------------
def load_zone_config():
    """Query rooms + appliance tables to build zone mappings.
    Returns:
        room_zones:  {room_id: zone_count}  e.g. {1: 2, 2: 1}
        appl_zones:  {esp_key: zone}        e.g. {'1e0': 0, '1e1': 1, '2e2': 0}
        ip_map:      {room_id: stream_url}
    """
    room_zones = {}
    appl_zones = {}
    ip_map     = {}
    try:
        with con.cursor() as cursor:
            cursor.execute("SELECT id, zone_count, ip, port FROM rooms")
            for r in cursor.fetchall():
                rid = r['id']
                room_zones[rid] = r['zone_count']
                if r['ip'] and r['port']:
                    ip_map[rid] = f"http://{r['ip']}:{r['port']}/stream"

            cursor.execute("SELECT id, room_id, zone FROM appliance")
            for a in cursor.fetchall():
                # Build all possible ESP key formats for this appliance
                esp_key = f"{a['room_id']}e{a['id']}"
                appl_zones[esp_key] = a['zone']
    except Exception as e:
        print(f"[DB ERROR] load_zone_config: {e}")
    return room_zones, appl_zones, ip_map


def get_person_zone(cx, frame_width, zone_count):
    """Given a person's center-x, frame width, and zone count, return which zone they are in.
    Zone layout:  zone 0 = left, zone 1 = middle (if 3 zones) or right (if 2), zone 2 = right
    """
    if zone_count <= 1:
        return 0
    zone_width = frame_width / zone_count
    zone = int(cx / zone_width)
    return min(zone, zone_count - 1)  # clamp to last zone


def count_people_per_zone(result_boxes, frame_width, zone_count):
    """Count people (class 0) in each zone. Returns dict {zone_idx: count}."""
    counts = {z: 0 for z in range(zone_count)}
    for box in result_boxes:
        if int(box.cls[0]) != 0:  # only count persons
            continue
        x1, _, x2, _ = box.xyxy[0].tolist()
        cx = (x1 + x2) / 2.0
        zone = get_person_zone(cx, frame_width, zone_count)
        counts[zone] += 1
    return counts


# Load zone config from DB
room_zones, appl_zones, ip_map = load_zone_config()
print(f"[ZONES] room_zones = {room_zones}")
print(f"[ZONES] appl_zones = {appl_zones}")
print(f"[ZONES] ip_map     = {ip_map}")

# ---------------------------------------------------------------------------
# WASTE TRACKING STATE  (keyed by appliance id e.g. "1e2")
# ---------------------------------------------------------------------------
TRIGGER_DELAY = 10   # seconds of empty zone before the trigger fires

waste_track: dict[str, dict] = {}   # populated dynamically as esp.json is read

wastage: list[dict] = []
room_status = {rid: 'empty' for rid in ip_map}

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------
CLASS_NAMES = {0: "person", 1: "face"}
COLORS      = {0: (56, 56, 255), 1: (10, 249, 72)}   # BGR

# ---------------------------------------------------------------------------
# MODEL INIT
# ---------------------------------------------------------------------------
model_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../ai/exp-3.pt'))
device     = 'cuda' if torch.cuda.is_available() else 'cpu'
model      = YOLO(model_path).to(device)

print(f"[Server] Model loaded on {model.device.type.upper()}")

# Open camera captures once
caps      = {room_id: cv2.VideoCapture(url) for room_id, url in ip_map.items()}
prev_time = {room_id: time.time() for room_id in ip_map}

# Frame throttling state: room_id -> timestamp
room_empty_since = {rid: None for rid in ip_map}
last_processed   = {rid: 0.0 for rid in ip_map}

print("[Server] Running... Press 'q' to quit.")

# ---------------------------------------------------------------------------
# MAIN LOOP
# ---------------------------------------------------------------------------
try:
    while True:
        # Re-read ESP state from disk every tick (live updates)
        esp_state = load_esp_state()

        # Ensure waste_track has entries for all known appliances
        for key in esp_state:
            if key not in waste_track:
                waste_track[key] = {"active": False, "time": None, "triggered": False}

        # Snapshot keys to avoid RuntimeError if caps dict changes mid-loop
        for room_id in list(caps.keys()):
            cap = caps[room_id]

            # ---------- reconnect if needed ----------
            if not cap.isOpened():
                print(f"[Server] Room {room_id} reconnecting...")
                caps[room_id] = cv2.VideoCapture(ip_map[room_id])
                continue

            # ---------- power saving throttle ----------
            # If room empty for > 60s, only process AI once per second
            now_loop = time.time()
            if room_empty_since.get(room_id) and (now_loop - room_empty_since[room_id] > 60):
                if (now_loop - last_processed.get(room_id, 0.0)) < 1.0:
                    cap.grab() # clear buffer but skip expensive decoding & AI
                    continue
            
            last_processed[room_id] = now_loop

            # ---------- grab freshest frame ----------
            cap.grab()
            ret, frame = cap.retrieve()

            if not ret:
                print(f"[Server] No frame from Room {room_id} — retrying next tick")
                cap.release()
                caps[room_id] = cv2.VideoCapture(ip_map[room_id])
                continue

            # ---------- AI inference ----------
            result = model.predict(
                frame, imgsz=320, conf=0.25, device=device, verbose=False
            )[0]
            people = sum(1 for b in result.boxes if int(b.cls[0]) == 0)
            frame_h, frame_w = frame.shape[:2]
            zone_count = room_zones.get(room_id, 1)

            # ---------- per-zone people count ----------
            zone_people = count_people_per_zone(result.boxes, frame_w, zone_count)

            # Update empty-time tracker (whole room)
            if people > 0:
                room_empty_since[room_id] = None
            else:
                if room_empty_since[room_id] is None:
                    room_empty_since[room_id] = time.time()

            if (people > 0) and (room_status[room_id] == 'empty'):
                room_status[room_id] = 'occupied'
                query = "UPDATE status SET status = 'occupied' WHERE room_id = %s"
                with con.cursor() as cursor:
                    cursor.execute(query, (room_id,))
                    con.commit()
                query = "UPDATE status SET p_count = %s WHERE room_id = %s"
                with con.cursor() as cursor:
                    cursor.execute(query, (people, room_id))
                    cursor.execute("INSERT INTO alerts (timestamp, room_id, info) VALUES (NOW(), %s, %s)", (room_id, f"Motion detected in Room {room_id}"))
                    con.commit()
            elif (people == 0) and (room_status[room_id] == 'occupied'):
                room_status[room_id] = 'empty'
                query = "UPDATE status SET status = 'empty' WHERE room_id = %s"
                with con.cursor() as cursor:
                    cursor.execute(query, (room_id,))
                    con.commit()
                query = "UPDATE status SET p_count = %s WHERE room_id = %s"
                with con.cursor() as cursor:
                    cursor.execute(query, (people, room_id))
                    cursor.execute("INSERT INTO alerts (timestamp, room_id, info) VALUES (NOW(), %s, %s)", (room_id, f"Room {room_id} is now empty"))
                    con.commit()

            # ---------- appliance state for this room ----------
            appliances = check_appl(esp_state, room_id)
            now        = time.time()

            # ---------- zone-aware waste logic ----------
            for appliance, is_on in appliances.items():
                state = waste_track[appliance]
                appl_zone = appl_zones.get(appliance, 0)   # which zone this appliance is in
                zone_empty = (zone_people.get(appl_zone, 0) == 0)  # is that zone empty?

                # START: zone empty and appliance on → begin tracking
                if zone_empty and is_on == 1 and not state["active"]:
                    state["active"]    = True
                    state["time"]      = now
                    state["triggered"] = False
                    print(f"[WASTE START]  {appliance} (zone {appl_zone}) left on in empty zone — Room {room_id}")

                # TRIGGER: still wasting — fire once after TRIGGER_DELAY seconds
                elif state["active"] and not state["triggered"] and (now - state["time"]) >= TRIGGER_DELAY:
                    state["triggered"] = True
                    elapsed = round(now - state["time"], 1)
                    print(f"[TRIGGER]      {appliance} (zone {appl_zone}) in Room {room_id} wasting for {elapsed}s — act now!")

                    try:
                        query = "INSERT INTO alerts (timestamp, room_id, info) VALUES (NOW(), %s, %s)"
                        info  = f"Wastage in Room {room_id} Zone {appl_zone} — {appliance} running with no occupancy"
                        with con.cursor() as cursor:
                            cursor.execute(query, (room_id, info))
                        con.commit()
                    except Exception as e:
                        print(f"[DB ERROR] Failed to insert alert: {e}")

                    try:
                        send_sms(f"Wastage in Room {room_id} Zone {appl_zone} — appliance {appliance} running with no occupancy")
                    except Exception as e:
                        print(f"[SMS ERROR] Failed to send SMS: {e}")

                    if automation:
                        threading.Timer(5.0, turn_off_appliance, args=[appliance]).start()
                        print(f"[AUTO] Scheduled turn-off in 5 seconds for {appliance}")

                # CANCEL: appliance turned off while zone is still empty
                elif is_on == 0 and zone_empty and state["active"]:
                    state["active"]    = False
                    state["time"]      = None
                    state["triggered"] = False
                    print(f"[WASTE CANCEL] {appliance} (zone {appl_zone}) turned off — Room {room_id}")

                # END + LOG: a person entered the appliance's zone while tracked → genuine waste
                elif not zone_empty and state["active"]:
                    duration_sec = now - state["time"]

                    record = {
                        "room":         room_id,
                        "zone":         appl_zone,
                        "appliance":    appliance,
                        "duration_sec": round(duration_sec, 2),
                        "duration_min": round(duration_sec / 60, 2),
                        "start_time":   state["time"],
                        "end_time":     now,
                    }
                    wastage.append(record)
                    print(f"[WASTE END]    {record}")
                    try:
                        app_id = int(appliance.split('e')[1])
                        loss = get_energy_loss(app_id, record["duration_min"])
                        if loss is not None:
                            query = "INSERT INTO energy (room_id, app_id, loss) VALUES (%s, %s, %s)"
                            with con.cursor() as cursor:
                                cursor.execute(query, (room_id, app_id, round(loss, 4)))
                            con.commit()
                    except Exception as e:
                        print(f"[WASTE END]    Error recording waste: {e}")
                    state["active"]    = False
                    state["time"]      = None
                    state["triggered"] = False

            fps                = 1.0 / max(now - prev_time[room_id], 1e-6)
            prev_time[room_id] = now


            for box in result.boxes:
                cls_id          = int(box.cls[0])
                conf            = float(box.conf[0])
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                color           = COLORS.get(cls_id, (200, 200, 200))
                label           = f"{CLASS_NAMES.get(cls_id, cls_id)} {conf:.2f}"

                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
                cv2.rectangle(frame, (x1, y1 - th - 5), (x1 + tw + 3, y1), color, -1)
                cv2.putText(frame, label, (x1 + 2, y1 - 3),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)

            # Draw zone dividers on frame
            if zone_count > 1:
                zone_w = frame_w // zone_count
                for zi in range(1, zone_count):
                    x = zi * zone_w
                    cv2.line(frame, (x, 0), (x, frame_h), (255, 255, 0), 1, cv2.LINE_AA)
                # Zone labels at the top
                zone_names = ["L", "M", "R"] if zone_count == 3 else ["L", "R"]
                for zi in range(zone_count):
                    zx = zi * zone_w + 6
                    ztxt = f"Z{zi}({zone_names[zi]}):{zone_people.get(zi,0)}p"
                    cv2.putText(frame, ztxt, (zx, frame_h - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 0), 1, cv2.LINE_AA)

            # HUD overlay
            appl_summary = "  ".join(
                f"{k}={'ON' if v else 'off'}" for k, v in appliances.items()
            )
            cv2.putText(frame,
                        f"Room {room_id} | People: {people} | Zones: {zone_count} | FPS: {fps:.1f}",
                        (10, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 0), 2, cv2.LINE_AA)
            cv2.putText(frame, appl_summary,
                        (10, 54), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 200, 255), 1, cv2.LINE_AA)

            cv2.imshow(f"Room {room_id} — Watt-Watch", frame)

            print(f"[Room {room_id}] People: {people} | Zones: {dict(zone_people)} | FPS: {fps:.1f}")

        # 'q' in any window quits
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        time.sleep(0.03)   # ~30 Hz cap; inference is the real limiter

except KeyboardInterrupt:
    print("\n[Server] Stopped by user.")

finally:
    # Reset all rooms in DB to 'empty' / 0 people so dashboard stays clean
    try:
        with con.cursor() as cursor:
            cursor.execute("UPDATE status SET status = 'empty', p_count = 0")
        con.commit()
        print("[Server] Database status reset to 'empty' for all rooms.")
    except Exception as e:
        print(f"[ERROR] Could not reset database status: {e}")

    for cap in caps.values():
        cap.release()
    cv2.destroyAllWindows()

    print("\n==== WASTAGE SUMMARY ====")
    for w in wastage:
        print(w)
    print(f"\n{len(wastage)} waste event(s) recorded.")

    sys.exit(0)