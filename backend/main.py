import socketio
import cv2
import numpy as np
import base64
import os
import time
import importlib.util
import queue

sio = socketio.Client(reconnection=True, logger=False, engineio_logger=False)

frame_queue = queue.Queue(maxsize=2)
running = True

@sio.on('frame')
def receive_frame(data):
    if not data:
        return

    if isinstance(data, (bytes, bytearray)):
        img = bytes(data)
    elif isinstance(data, str):
        try:
            img = base64.b64decode(data, validate=True)
        except Exception:
            print("Warning: received invalid base64 frame payload")
            return
    else:
        print(f"Warning: unexpected frame payload type: {type(data)}")
        return

    np_arr = np.frombuffer(img, np.uint8)
    frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    if frame is None or frame.size == 0:
        print("Warning: failed to decode incoming frame")
        return

    # Put frame in queue. If queue is full, remove the oldest unread frame to avoid lag latency.
    try:
        if frame_queue.full():
            frame_queue.get_nowait()
        frame_queue.put_nowait(frame)
    except queue.Empty:
        pass
    except queue.Full:
        pass


@sio.on('disconnect')
def on_disconnect():
    global running
    running = False
    print("Disconnected from server.")


@sio.on('connect')
def on_connect():
    print("Connected to stream server")


@sio.on('connect_error')
def on_connect_error(data):
    print(f"Connect error: {data}")


server_url = os.getenv('STREAM_SERVER_URL', 'http://127.0.0.1:5000')
has_websocket_client = importlib.util.find_spec('websocket') is not None
transports = ['websocket', 'polling'] if has_websocket_client else ['polling']
print(f"Connecting to {server_url} using transports={transports}")

last_error = None
for attempt in range(1, 6):
    try:
        sio.connect(server_url, transports=transports, wait_timeout=10)
        break
    except Exception as exc:
        last_error = exc
        print(f"Connection attempt {attempt}/5 failed: {exc}")
        time.sleep(1)
else:
    raise SystemExit(
        f"Unable to connect to {server_url}. "
        "Ensure server is running and STREAM_SERVER_URL is correct. "
        f"Last error: {last_error}"
    )

try:
    while running:
        frame_to_show = None
        try:
            # Safely grab the newest frame from the queue (non-blocking)
            frame_to_show = frame_queue.get_nowait()
        except queue.Empty:
            pass

        if frame_to_show is not None:
            cv2.imshow("Stream", frame_to_show)

        # 30ms wait provides ~33 FPS GUI refresh rate
        if cv2.waitKey(30) == 27:  # ESC key
            break
finally:
    running = False
    sio.disconnect()
    cv2.destroyAllWindows()