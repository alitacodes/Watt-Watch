import cv2
from flask import Flask, Response
import socket
import time

app = Flask(__name__)
camera = cv2.VideoCapture(0)          # 0 = first webcam


def generate_frames(frame_rate=12,camera=camera,frame_width=640,frame_height=320):
    camera.set(cv2.CAP_PROP_FRAME_WIDTH,  frame_width)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_height)
    target_fps = frame_rate
    min_frame_time = 1.0 / target_fps
    last_yield_time = 0

    while True:
        success, frame = camera.read()
        if not success:
            break

        # Drop frames to enforce software FPS cap and prevent lag buffering
        current_time = time.time()
        if (current_time - last_yield_time) < min_frame_time:
            continue
            
        last_yield_time = current_time

        # Encode frame as JPEG
        _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
        frame_bytes = buffer.tobytes()

        # MJPEG multipart format — standard for IP cameras
        yield (
            b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n'
            + frame_bytes +
            b'\r\n'
        )

@app.route('/stream')
def stream():
    return Response(
        generate_frames(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )

@app.route('/')
def index():
    ip = socket.gethostbyname(socket.gethostname())
    return f"""
    <h3>Camera streamer running</h3>
    <p>Stream URL: <code>http://{ip}:5000/stream</code></p>
    <img src="/stream" width="640">
    """

def start_camera_stream(host='0.0.0.0', port=5000):
    ip = socket.gethostbyname(socket.gethostname())
    print(f"[Camera] Streaming at http://{ip}:{port}/stream")
    print(f"[Camera] Preview at  http://{ip}:{port}")
    app.run(host=host, port=port, threaded=True)


if __name__ == '__main__':
    port = 5002
    ip = socket.gethostbyname(socket.gethostname())
    print(f"[Camera] Streaming at http://{ip}:{port}/stream")
    print(f"[Camera] Preview at  http://{ip}:{port}")
    app.run(host='0.0.0.0', port=port, threaded=True)