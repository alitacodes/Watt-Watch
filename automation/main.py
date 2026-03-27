import cv2
import time
import os
import sys
import json
import torch
from ultralytics import YOLO
import pymysql
from dotenv import load_dotenv

from twilio.rest import Client



load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT", 25060))
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME")
TW_SID = os.getenv("TW_SID")
TW_AUTH_TOKEN = os.getenv("TW_AUTH_TOKEN")

def send_sms(body):
    account_sid = TW_SID
    auth_token = TW_AUTH_TOKEN
    client = Client(account_sid, auth_token)
    message = client.messages.create(
    from_='+14788003912',
    body=body,
    to='+919330588689'
    )
    print(message.sid)



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
# WASTE TRACKING STATE  (keyed by appliance id e.g. "1e2")
# ---------------------------------------------------------------------------
TRIGGER_DELAY = 10   # seconds of empty room before the trigger fires

waste_track: dict[str, dict] = {}   # populated dynamically as esp.json is read

wastage: list[dict] = []
room_status = {1:'empty',2:'empty'}

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------
CLASS_NAMES = {0: "person", 1: "face"}
COLORS      = {0: (56, 56, 255), 1: (10, 249, 72)}   # BGR

ip_map = {
    1: "http://192.168.56.1:5001/stream",
    2: "http://192.168.56.1:5002/stream",
}

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
            if (people > 0) and (room_status[room_id] == 'empty'):
                room_status[room_id] = 'occupied'
                query = "UPDATE status SET status = 'occupied' WHERE room_id = %s"
                with con.cursor() as cursor:
                    cursor.execute(query, (room_id,))
                    con.commit()
            elif (people == 0) and (room_status[room_id] == 'occupied'):
                room_status[room_id] = 'empty'
                query = "UPDATE status SET status = 'empty' WHERE room_id = %s"
                with con.cursor() as cursor:
                    cursor.execute(query, (room_id,))
                    con.commit()
                    
                

            # ---------- appliance state for this room ----------
            appliances = check_appl(esp_state, room_id)
            now        = time.time()

            # ---------- waste logic ----------
            for appliance, is_on in appliances.items():
                state = waste_track[appliance]

                # START: room empty and appliance on → begin tracking
                if people == 0 and is_on == 1 and not state["active"]:
                    state["active"]    = True
                    state["time"]      = now
                    state["triggered"] = False
                    print(f"[WASTE START]  {appliance} left on in empty Room {room_id}")

                # TRIGGER: still wasting — fire once after TRIGGER_DELAY seconds
                elif state["active"] and not state["triggered"] and (now - state["time"]) >= TRIGGER_DELAY:
                    state["triggered"] = True
                    elapsed = round(now - state["time"], 1)
                    print(f"[TRIGGER]      {appliance} in Room {room_id} wasting for {elapsed}s — act now!")

                    try:
                        query = "INSERT INTO alerts (timestamp, room_id, info) VALUES (NOW(), %s, %s)"
                        info  = f"Wastage found in empty room {room_id}"
                        with con.cursor() as cursor:
                            cursor.execute(query, (room_id, info))
                        con.commit()
                    except Exception as e:
                        print(f"[DB ERROR] Failed to insert alert: {e}")

                    try:
                        send_sms(f"Wastage found in empty room {room_id}")
                    except Exception as e:
                        print(f"[SMS ERROR] Failed to send SMS: {e}")
                    # ── Put your action here ──────────────────────────────────
                    # e.g. requests.get(f"http://esp-ip/off?id={appliance}")
                    # ─────────────────────────────────────────────────────────

                # CANCEL: appliance turned off while room is still empty
                # → someone switched it off remotely, nothing was wasted
                elif is_on == 0 and people == 0 and state["active"]:
                    state["active"]    = False
                    state["time"]      = None
                    state["triggered"] = False
                    print(f"[WASTE CANCEL] {appliance} turned off while Room {room_id} still empty — not waste")

                # END + LOG: a person entered while appliance was tracked → genuine waste
                elif people > 0 and state["active"]:
                    duration_sec = now - state["time"]

                    record = {
                        "room":         room_id,
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
                # label background
                (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
                cv2.rectangle(frame, (x1, y1 - th - 5), (x1 + tw + 3, y1), color, -1)
                cv2.putText(frame, label, (x1 + 2, y1 - 3),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)

            # HUD overlay
            appl_summary = "  ".join(
                f"{k}={'ON' if v else 'off'}" for k, v in appliances.items()
            )
            cv2.putText(frame,
                        f"Room {room_id} | People: {people} | FPS: {fps:.1f}",
                        (10, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 0), 2, cv2.LINE_AA)
            cv2.putText(frame, appl_summary,
                        (10, 54), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 200, 255), 1, cv2.LINE_AA)

            cv2.imshow(f"Room {room_id} — Watt-Watch", frame)

            print(f"[Room {room_id}] People: {people} | FPS: {fps:.1f}")

        # 'q' in any window quits
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        time.sleep(0.03)   # ~30 Hz cap; inference is the real limiter

except KeyboardInterrupt:
    print("\n[Server] Stopped by user.")

finally:
    for cap in caps.values():
        cap.release()
    cv2.destroyAllWindows()

    print("\n==== WASTAGE SUMMARY ====")
    for w in wastage:
        print(w)
    print(f"\n{len(wastage)} waste event(s) recorded.")

    sys.exit(0)