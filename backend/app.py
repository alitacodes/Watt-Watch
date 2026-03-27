from flask import Flask, request, jsonify, Response, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from db import get_db_connection

from ultralytics import YOLO
import torch

import pymysql
import logging
import os
from dotenv import load_dotenv
import cv2
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

# (You can easily add more dedicated routes like above)
# e.g.:
# @app.route('/settings')
# @login_required
# def settings():
#     return app.send_static_file('index.html')

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
    print(result)
    if result is None:
        return {"exists": False}
    return {"exists": True}

# ---- Admin-Only Endpoints ----
@app.get('/api/v1/users')
@login_required
@require_role('admin')
def get_all_users():
    """Admin only: Get list of all users"""
    try:
        with con.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("SELECT userid, type FROM users")
            users = cursor.fetchall()
        return jsonify({"users": users}), 200
    except pymysql.MySQLError as e:
        logging.error(f"Error fetching users: {e}")
        return jsonify({"error": "Failed to fetch users"}), 500

@app.post('/api/v1/delete_user/<userid>')
@login_required
@require_role('admin')
def delete_user(userid):
    """Admin only: Delete a user"""
    try:
        with con.cursor() as cursor:
            cursor.execute("DELETE FROM users WHERE userid = %s", (userid,))
        con.commit()
        return jsonify({"message": "User deleted successfully"}), 200
    except pymysql.MySQLError as e:
        logging.error(f"Error deleting user: {e}")
        return jsonify({"error": "Failed to delete user"}), 500

# ---- Mod-Only Endpoints ----
@app.get('/api/v1/recent_activity')
@login_required
@require_role('admin', 'mod')
def recent_activity():
    """Admin & Mod only: Get recent activity logs"""
    return jsonify({"activity": "Recent activity data"}), 200

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
def get_video(ip, port, ):
    # For GET requests (e.g. from <img src="...">), body is usually empty. We should use query args or handle missing JSON gracefully.
    body = request.get_json(silent=True) or {}
    
    # Check if client is explicitly asking for redaction to be turned off. Default is true.
    wants_unredacted = request.args.get('redact', 'true').lower() == 'false' or body.get('redact') == False
    
    # Always default to True until we positively verify they have admin rights
    
    cap = connect_camera(f"http://{ip}:{port}/stream")
    model = YOLO(model_path).to(device)
    def generate_frames():
        while True:
            success, frame = cap.read()
            if not success:
                break
            results = model.predict(frame, conf=0.15, verbose=False, device=device, imgsz=320, iou=0.2)[0]
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

@app.get("/video/<ip>/<port>/admin")
@login_required
@require_role('admin')
def get_video_admin(ip, port):
    cap = connect_camera(f"http://{ip}:{port}/stream")

    def generate_frames():
        while True:
            success, frame = cap.read()
            if not success:
                break
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