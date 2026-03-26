from flask import Flask, request, jsonify, Response, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from db import get_db_connection

from ultralytics import YOLO

import pymysql
import logging
import os
from dotenv import load_dotenv
import cv2
from cam import connect_camera, redaction


load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT", 25060))
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME")

con = get_db_connection()

app = Flask(__name__, static_folder='../frontend/public', static_url_path='/')
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "super-secret-change-me")

# --- 1. Flask-Login Setup ---
login_manager = LoginManager()
login_manager.init_app(app)

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


# SPA configuration: serve index.html for all non-API routes
@app.route('/', defaults={'path': ''})
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

@app.post('/api/v1/logout')
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
    print(result)
    if result is None:
        return {"exists": False}
    return {"exists": True}

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

        
@app.get("/video/<ip>/<port>/<redact_state>")
@login_required
def get_video(ip, port, redact_state):
    # For GET requests (e.g. from <img src="...">), body is usually empty. We should use query args or handle missing JSON gracefully.
    body = request.get_json(silent=True) or {}
    
    # Check if client is explicitly asking for redaction to be turned off. Default is true.
    wants_unredacted = request.args.get('redact', 'true').lower() == 'false' or body.get('redact') == False
    
    # Always default to True until we positively verify they have admin rights
    redact = True 
    
    if wants_unredacted:
        try:
            with con.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute("SELECT userid FROM users WHERE type = 'admin'")
                admin_list = [row['userid'] for row in cursor.fetchall()]
                
            username = body.get('username') or current_user.id
            
            # Positively confirm the user is in the admin list before turning off redaction
            if username in admin_list:
                redact = False
        except Exception as e:
            print("Warning: Could not verify user for redaction. Defaulting to redaction ON.", getattr(e, 'message', str(e)))
            redact = True
    if redact_state in ("false",'0'):
        redact = False
    cap = connect_camera(f"http://{ip}:{port}/stream")
    model_path = "/home/ankan/projects/frost/exp-3.pt"
    model = YOLO(model_path).to('cuda')
    def generate_frames():
        while True:
            success, frame = cap.read()
            if not success:
                break
            results = model.predict(frame, conf=0.15, verbose=False, device='cuda', imgsz=320, iou=0.2)[0]
            if redact:
                for box_obj in results.boxes:
                    cls_id = int(box_obj.cls[0])
                    if cls_id == 1:
                        redaction(frame, box_obj.xyxy[0].tolist(), cls_id, float(box_obj.conf[0]))
            ret, buffer = cv2.imencode('.jpg', frame)
            if not ret:
                continue
                
            frame_bytes = buffer.tobytes()
            yield (
                b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n'
            )

    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)