from flask import Flask, request, jsonify, Response, redirect, url_for, send_file
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from db import get_db_connection

from ultralytics import YOLO
import torch

import pymysql
import logging
import os
import csv
import io
from datetime import datetime, timedelta
from dotenv import load_dotenv
import cv2
import time
from functools import wraps
from cam import connect_camera, redaction


load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT", 25060))
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME")

con = get_db_connection()
model_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../ai/exp-3.pt'))
device = 'cuda' if torch.cuda.is_available() else 'cpu'

app = Flask(__name__, static_folder='../frontend/public', static_url_path='/')
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "super-secret-change-me")

# --- 1. Flask-Login Setup ---
login_manager = LoginManager()
login_manager.init_app(app)
# ---- Role-Based Access Control Decorator ----
def require_role(*allowed_roles):
    """Decorator to check if user has one of the allowed roles"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return jsonify({"error": "Unauthorized"}), 401
            if current_user.user_type not in allowed_roles:
                return jsonify({"error": "Forbidden - insufficient permissions"}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator


class User(UserMixin):
    def __init__(self, userid, user_type):
        self.id = userid       # Maps to 'userid' in your table
        self.user_type = user_type # Maps to 'type' in your table
        

@login_manager.user_loader
def load_user(user_id):
    con = get_db_connection()
    try:
        with con.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("SELECT userid, type FROM users WHERE userid = %s", (user_id,))
            user_data = cursor.fetchone()
            if user_data:
                return User(userid=user_data['userid'], user_type=user_data['type'])
            return None
    finally:
        con.close()

# ---- Dedicated Web Routes ----
@app.route('/')
def home():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    return app.send_static_file('index.html')

@app.route('/login')
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return app.send_static_file('index.html')

@app.route('/dashboard')
@login_required
@require_role('admin', 'mod')
def dashboard():
    return app.send_static_file('index.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return app.send_static_file('index.html')

@app.route('/rooms')
@login_required
def rooms_page():
    return app.send_static_file('index.html')

@app.route('/report')
@login_required
def report_page():
    return app.send_static_file('index.html')

# Catch-all to still serve CSS/JS (needed so Svelte can load its assets)
@app.route('/<path:path>')
def catch_all(path):
    if path.startswith('api/'):
        return jsonify({"error": "Not Found"}), 404
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return app.send_static_file(path)
    return app.send_static_file('index.html')

#-----api -----

@app.get('/api/v1/auth/status')
def auth_status():
    if current_user.is_authenticated:
        return jsonify({"authenticated": True, "userid": current_user.id, "type": current_user.user_type}), 200
    return jsonify({"authenticated": False}), 401

@app.post('/api/v1/login')
def login_api():
    data = request.get_json()
    username_input = data.get('userid')
    password_input = data.get('password')

    if not username_input or not password_input:
        return jsonify({"error": "Missing credentials"}), 400

    con = get_db_connection()
    try:
        with con.cursor(pymysql.cursors.DictCursor) as cursor:
            # Simple check against your 'users' table
            query = "SELECT userid, password, type FROM users WHERE userid = %s"
            cursor.execute(query, (username_input,))
            user_data = cursor.fetchone()

            # Verify existence and password (raw string check as requested)
            if user_data and user_data['password'] == password_input:
                user_obj = User(userid=user_data['userid'], user_type=user_data['type'])
                
                # This function handles the creation of the session cookie
                login_user(user_obj)
                
                return jsonify({"message": "Login successful", "userid": user_obj.id}), 200
            
            return jsonify({"error": "Invalid userid or password"}), 401
    finally:
        con.close()

@app.route('/api/v1/logout')
@login_required
def logout_api():
    logout_user()
    return jsonify({"message": "Logged out"}), 200


@app.get('/api/v1/check_user/<userid>')
def check_user(userid):
    query = "SELECT userid FROM users WHERE userid = %s"
    with con.cursor() as cursor:
        cursor.execute(query, (userid,))
        result = cursor.fetchone()
    if result is None:
        return {"exists": False}
    return {"exists": True}
@app.get("/api/v1/stats")
@login_required
def get_stats():
    con_local = get_db_connection()
    try:
        with con_local.cursor() as cursor:
            # Total rooms
            cursor.execute("SELECT COUNT(*) AS total FROM rooms")
            total_rooms = cursor.fetchone()['total']

            # Total waste kW today (sum of energy loss for today)
            cursor.execute(
                "SELECT COALESCE(SUM(loss), 0) AS total_waste FROM energy WHERE DATE(miniute) = CURDATE()"
            )
            waste_kw = float(cursor.fetchone()['total_waste'])

            # Total kW: sum of wattage of all appliances / 1000
            cursor.execute("SELECT COALESCE(SUM(wattage), 0) AS total_w FROM appliance")
            total_kw = round(cursor.fetchone()['total_w'] / 1000, 2)

        return jsonify({
            "totalRooms": total_rooms,
            "wasteKw": round(waste_kw, 2),
            "totalKw": total_kw
        })
    finally:
        con_local.close()


@app.get("/api/v1/alerts")
@login_required
def get_alerts():
    con_local = get_db_connection()
    try:
        with con_local.cursor() as cursor:
            # Fetch alerts from the last 3 minutes
            cursor.execute("""
                SELECT id, timestamp, room_id, info
                FROM alerts
                WHERE timestamp >= NOW() - INTERVAL 3 MINUTE
                ORDER BY timestamp DESC
            """)
            alerts = cursor.fetchall()
            
            # Format results for the frontend
            formatted_alerts = []
            for a in alerts:
                msg = a['info'].lower()
                status = "warning" # Default
                
                if "motion" in msg or "occupied" in msg:
                    status = "occupied"
                elif "empty" in msg or "cleared" in msg or "vacant" in msg:
                    status = "vacant"
                elif "wastage" in msg or "warning" in msg:
                    status = "warning"
                
                # Format the time as HH:MM
                time_str = a['timestamp'].strftime('%H:%M') if a['timestamp'] else "--:--"
                
                formatted_alerts.append({
                    "id": a['id'],
                    "room_id": a['room_id'],
                    "status": status,
                    "message": a['info'],
                    "time": time_str
                })
                
        return jsonify({"alerts": formatted_alerts})
    finally:
        con_local.close()


@app.get("/api/v1/rooms")
@app.get("/api/v1/room_list/")
@login_required
def get_rooms_list():
    con_local = get_db_connection()
    try:
        with con_local.cursor() as cursor:
            # Fetch all rooms
            cursor.execute("SELECT * FROM rooms")
            rooms = cursor.fetchall()

            # Build a status lookup: room_id -> {status, p_count}
            cursor.execute("SELECT room_id, status, p_count FROM status")
            status_rows = cursor.fetchall()
            status_map = {r['room_id']: {"status": r['status'], "p_count": r.get('p_count', 0)} for r in status_rows}

            # Build current_usage_kw: sum of wattage per room / 1000
            cursor.execute("SELECT room_id, SUM(wattage) AS total_w FROM appliance GROUP BY room_id")
            usage_rows = cursor.fetchall()
            usage_map = {r['room_id']: round(r['total_w'] / 1000, 2) for r in usage_rows}

            # Daily energy loss per room
            cursor.execute("""
                SELECT room_id, COALESCE(SUM(loss), 0) AS daily_kwh
                FROM energy
                WHERE DATE(miniute) = CURDATE()
                GROUP BY room_id
            """)
            daily_map = {r['room_id']: float(r['daily_kwh']) for r in cursor.fetchall()}

            # Monthly energy loss per room
            cursor.execute("""
                SELECT room_id, COALESCE(SUM(loss), 0) AS monthly_kwh
                FROM energy
                WHERE YEAR(miniute) = YEAR(CURDATE()) AND MONTH(miniute) = MONTH(CURDATE())
                GROUP BY room_id
            """)
            monthly_map = {r['room_id']: float(r['monthly_kwh']) for r in cursor.fetchall()}

        for room in rooms:
            rid = room['id']
            room['room_id'] = rid
            s_data = status_map.get(rid, {"status": "unknown", "p_count": 0})
            room['status'] = s_data['status']
            room['p_count'] = s_data['p_count']
            room['current_usage_kw'] = usage_map.get(rid, 0)
            room['daily_usage_kwh'] = round(daily_map.get(rid, 0), 3)
            room['monthly_usage_kwh'] = round(monthly_map.get(rid, 0), 3)
            # Aliases for wastage-focused views
            room['daily_wastage_kwh'] = room['daily_usage_kwh']
            room['monthly_wastage_kwh'] = room['monthly_usage_kwh']

        return jsonify({"rooms": rooms})
    finally:
        con_local.close()


@app.get("/api/v1/room/<room_id>")
@login_required
def room_details(room_id):
    query = "SELECT * FROM rooms WHERE id = %s"
    with con.cursor() as cursor:
        cursor.execute(query, (room_id,))
        result = cursor.fetchone()
    if result is None:
        return jsonify({"error": "Room not found"}), 404
    data = result
    query = "select * from appliance where room_id = %s"
    with con.cursor() as cursor:
        cursor.execute(query, (room_id,))
        result = cursor.fetchall()
    data["appliance"] = result
    return jsonify(data)

@app.get("/api/v1/room/daily_loss/<room_id>")
@login_required
def room_daily_loss(room_id):
    query = "SELECT * FROM energy WHERE room_id = %s AND DATE(miniute) = CURDATE()"
    with con.cursor() as cursor:
        cursor.execute(query, (room_id,))
        result = cursor.fetchall()
    total = 0
    for i in result:
        total += i["loss"]
    return jsonify({"total_loss": total})

@app.get("/api/v1/room/daily_loss_app/<room_id>")
@login_required
def room_daily_los_app(room_id):
    query = "SELECT * FROM energy WHERE room_id = %s AND DATE(miniute) = CURDATE()"
    with con.cursor() as cursor:
        cursor.execute(query, (room_id,))
        result = cursor.fetchall()
    total = {}
    app_id = []
    for i in result:
        if i['app_id']   not in app_id:
            app_id.append(i['app_id'])
            total[i['app_id']] = 0
        total[i['app_id']] += i['loss']
    return jsonify(total)

@app.post("/api/v1/add_room")
def add_room():
    request_data = request.get_json()
    try:
        no_of_appl = request_data['no_of_appl']
        zone_count = request_data['zone_count']
        appl = request_data['appl']
        ip = request_data.get('ip', None)
        port = int(request_data['port']) if request_data.get('port') is not None else None
    except Exception as e:
        return jsonify({"error": "invalid request"}), 400

    try:
        with con.cursor() as cursor:
            # Insert room and get the new room_id
            query = "INSERT INTO rooms (no_of_appl, zone_count, ip, port) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, (no_of_appl, zone_count, ip, port))
            room_id = cursor.lastrowid
            
            # Insert each appliance belonging to this new room
            for i in appl:
                app_query = "INSERT INTO appliance (room_id, wattage, type, zone) VALUES (%s, %s, %s, %s)"
                cursor.execute(app_query, (room_id, i['wattage'], i['type'], i['zone']))
            
        con.commit()
        return jsonify({"message": "Room added successfully", "room_id": room_id}), 200
    except pymysql.MySQLError as e:
        con.rollback()
        logging.error(f"Error adding room: {e}")
        return jsonify({"error": "Database error"}), 500

# ---- Report APIs ----

@app.get("/api/v1/wastage/weekly")
@login_required
def weekly_wastage():
    """Return daily total wastage (all rooms summed) for the last 7 days."""
    con_local = get_db_connection()
    try:
        with con_local.cursor() as cursor:
            cursor.execute("""
                SELECT DATE(miniute) AS day, COALESCE(SUM(loss), 0) AS total_wh
                FROM energy
                WHERE DATE(miniute) >= CURDATE() - INTERVAL 6 DAY
                GROUP BY DATE(miniute)
                ORDER BY day ASC
            """)
            rows = cursor.fetchall()

        # Build a full 7-day series (fill missing days with 0)
        today = datetime.now().date()
        day_map = {}
        for r in rows:
            day_map[r['day']] = round(float(r['total_wh']), 4)

        result = []
        for i in range(6, -1, -1):
            d = today - timedelta(days=i)
            result.append({
                "date": d.isoformat(),
                "label": d.strftime("%a"),   # Mon, Tue, ...
                "wastage_wh": day_map.get(d, 0)
            })

        return jsonify({"weekly": result})
    finally:
        con_local.close()


@app.get("/api/v1/wastage/csv/<int:room_id>")
@login_required
def download_room_csv(room_id):
    """Download a CSV of daily wastage for a room over the last 30 days."""
    con_local = get_db_connection()
    try:
        with con_local.cursor() as cursor:
            cursor.execute("""
                SELECT DATE(miniute) AS day, COALESCE(SUM(loss), 0) AS total_wh
                FROM energy
                WHERE room_id = %s AND DATE(miniute) >= CURDATE() - INTERVAL 29 DAY
                GROUP BY DATE(miniute)
                ORDER BY day ASC
            """, (room_id,))
            rows = cursor.fetchall()

        # Build a full 30-day series
        today = datetime.now().date()
        day_map = {}
        for r in rows:
            day_map[r['day']] = round(float(r['total_wh']), 4)

        output = io.StringIO()
        # UTF-8 BOM so Excel opens the file correctly
        output.write('\ufeff')
        writer = csv.writer(output)
        writer.writerow(["Date", "Wastage (Wh)"])
        for i in range(29, -1, -1):
            d = today - timedelta(days=i)
            # Use DD/MM/YYYY format which Excel auto-sizes properly
            writer.writerow([d.strftime("%d/%m/%Y"), day_map.get(d, 0)])

        output.seek(0)
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={
                'Content-Disposition': f'attachment; filename=room-{room_id}-wastage-report.csv'
            }
        )
    finally:
        con_local.close()


# ---- Mod-Only Endpoints ----

@app.post('/api/v1/add_user/<userid>')
def add_user(userid):
    request_data = request.get_json()
    password = request_data.get("password")
    type = request_data.get("type")
    query = "INSERT INTO users (userid, password, type) VALUES (%s, %s, %s)"
    try:
        with con.cursor() as cursor:
            cursor.execute(query, (userid, password, type))
        con.commit()
        return jsonify({"message": "User added successfully"}), 200
    except pymysql.MySQLError as e:
        logging.error(f"Error adding user to database: {e}")
        return jsonify({"error": "Failed to add user"}), 500


@app.get("/video/<ip>/<port>/")
@login_required
def get_video(ip, port):
    try:
        cap = connect_camera(f"http://{ip}:{port}/stream")
    except ConnectionError:
        return jsonify({"error": "Camera not connected"}), 503
    model = YOLO(model_path).to(device)
    def generate_frames():
        prev_time = time.time()
        while True:
            success, frame = cap.read()
            if not success:
                break
            results = model.predict(frame, conf=0.15, verbose=False, device=device, imgsz=320, iou=0.25)[0]
            for box_obj in results.boxes:
                cls_id = int(box_obj.cls[0])
                if cls_id == 1:
                    redaction(frame, box_obj.xyxy[0].tolist(), cls_id, float(box_obj.conf[0]))

            # Calculate and draw FPS
            curr_time = time.time()
            fps = 1.0 / (curr_time - prev_time) if (curr_time - prev_time) > 0 else 0
            prev_time = curr_time
            cv2.putText(frame, f"FPS: {fps:.1f}", (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Remove the stray "# Calculate FPS" comment if it was there
            # (In your current file it's at line 248)

            ret, buffer = cv2.imencode('.jpg', frame)
            if not ret:
                continue
                
            frame_bytes = buffer.tobytes()
            yield (
                b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n'
            )

    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.get("/video/<ip>/<port>/admin")
@login_required
@require_role('admin')
def get_video_admin(ip, port):
    cap = connect_camera(f"http://{ip}:{port}/stream")

    def generate_frames():
        prev_time = time.time()
        while True:
            success, frame = cap.read()
            if not success:
                break
            
            curr_time = time.time()
            fps = 1.0 / (curr_time - prev_time) if (curr_time - prev_time) > 0 else 0
            prev_time = curr_time

            cv2.putText(frame, f"FPS: {fps:.1f}", (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            ret, buffer = cv2.imencode('.jpg', frame)
            if not ret:
                continue
            
            frame_bytes = buffer.tobytes()
            yield (
                b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n'
            )

    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


states = {
    "1e1": 0, "1e2": 0, "1e6": 0, # Room 1
    "2e3": 0, "2e4": 0, "2e5": 0  # Room 2
}

@app.route('/sync', methods=['POST'])
def sync():
    # ESP32 pings this to get the current "Source of Truth"
    return jsonify(states)

# New URL Format to match your request: /<room>/<appliance>/<state>
# Example: /2/e4/1 -> Key becomes "2e4"
@app.route('/<room>/<appliance>/<int:state>')
def update_state(room, appliance, state):
    key = f"{room}{appliance}"
    if key in states:
        states[key] = state
        print(f"[System] {key} is now {'ON' if state == 1 else 'OFF'}")
        return jsonify({"status": "success", "device": key, "state": state})
    return jsonify({"status": "error", "message": "Invalid mapping"}), 404



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)