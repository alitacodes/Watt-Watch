from flask import Flask, request, jsonify, Response
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

@app.route('/')
def index():
    return app.send_static_file('index.html')

# Catch-all route for SPA (Svelte Router)
@app.route('/<path:path>')
def catch_all(path):
    if os.path.exists(os.path.join(app.static_folder, path)):
        return app.send_static_file(path)
    return app.send_static_file('index.html')

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

        
@app.get("/video/<ip>/<port>")
def get_video(ip, port):
    body = request.get_json()
    redact = True
    try:
        if body['redact'] == False:
            admin_list = con.query("SELECT userid FROM users WHERE type = 'admin'")
            if admin_list is not None:
                if body['username'] in admin_list:
                    redact = False
    except Exception as e:
        print("Warning: Could not verify user for redaction. Defaulting to redaction ON.")
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