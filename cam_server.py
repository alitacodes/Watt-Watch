import cv2
import threading
import time
import socket
from flask import Flask, Response
from werkzeug.serving import make_server

# ---------------------------------------------------------------------------
# CameraStream — one capture thread, all ports/clients share the same frame
# ---------------------------------------------------------------------------
class CameraStream:
    def __init__(self, src=0, frame_rate=12, width=640, height=320, jpeg_quality=70):
        self.src          = src
        self.frame_rate   = frame_rate
        self.width        = width
        self.height       = height
        self.jpeg_quality = jpeg_quality

        self._lock        = threading.Lock()
        self._frame_bytes = None
        self._frame_event = threading.Event()
        self._running     = False

    def start(self):
        if self._running:
            return self
        self._running = True
        t = threading.Thread(target=self._capture_loop, daemon=True)
        t.start()
        return self

    def stop(self):
        self._running = False

    def _capture_loop(self):
        cap = cv2.VideoCapture(self.src)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH,  self.width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)

        min_frame_time = 1.0 / self.frame_rate
        last_time = 0

        while self._running:
            success, frame = cap.read()
            if not success:
                time.sleep(0.05)
                continue

            now = time.time()
            if (now - last_time) < min_frame_time:
                continue
            last_time = now

            _, buffer = cv2.imencode(
                '.jpg', frame,
                [cv2.IMWRITE_JPEG_QUALITY, self.jpeg_quality]
            )
            with self._lock:
                self._frame_bytes = buffer.tobytes()

            self._frame_event.set()
            self._frame_event.clear()

        cap.release()

    def generate(self):
        """Per-client generator — blocks until the next frame is ready."""
        while True:
            self._frame_event.wait(timeout=1.0)
            with self._lock:
                data = self._frame_bytes
            if data is None:
                continue
            yield (
                b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n'
                + data +
                b'\r\n'
            )


# ---------------------------------------------------------------------------
# Shared broadcaster — one camera, opened exactly once
# ---------------------------------------------------------------------------
broadcaster = CameraStream(src=0, frame_rate=12, width=640, height=320)


# ---------------------------------------------------------------------------
# Flask app shared across all ports
# ---------------------------------------------------------------------------
app = Flask(__name__)

@app.route('/stream')
def stream():
    return Response(
        broadcaster.generate(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )

@app.route('/')
def index():
    ip = socket.gethostbyname(socket.gethostname())
    return f"""
    <h3>Camera streamer running</h3>
    <p>Stream available on every bound port at <code>/stream</code></p>
    <img src="/stream" width="640">
    """


# ---------------------------------------------------------------------------
# Serve one Flask app on multiple ports simultaneously
# ---------------------------------------------------------------------------
def _serve_on_port(host, port):
    """Runs a blocking werkzeug server for the shared Flask app on one port."""
    server = make_server(host, port, app, threaded=True)
    ip = socket.gethostbyname(socket.gethostname())
    print(f"[Camera] Port {port} → http://{ip}:{port}/stream")
    server.serve_forever()


def start_camera_stream(host='0.0.0.0', ports=(5001,)):
    """
    Start the shared camera broadcaster and bind the stream to every port in
    `ports`.  All ports serve identical frames from the same physical camera.

    Examples
    --------
    # Single port (default behaviour)
    start_camera_stream(ports=(5001,))

    # Same feed on three ports at once
    start_camera_stream(ports=(5001, 5002, 5003))
    """
    broadcaster.start()

    if len(ports) == 1:
        # Blocking — no extra threads needed
        _serve_on_port(host, ports[0])
    else:
        # Spin up one thread per port; all threads are daemon threads so they
        # die automatically when the main program exits.
        threads = []
        for port in ports:
            t = threading.Thread(
                target=_serve_on_port,
                args=(host, port),
                daemon=True,
                name=f"cam-server-{port}"
            )
            t.start()
            threads.append(t)

        # Keep the main thread alive
        print(f"[Camera] Broadcasting on {len(ports)} ports. Press Ctrl+C to stop.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            broadcaster.stop()
            print("[Camera] Stopped.")


# ---------------------------------------------------------------------------
if __name__ == '__main__':
    # Edit this list to add or remove ports
    start_camera_stream(host='0.0.0.0', ports=(5001, 5002))