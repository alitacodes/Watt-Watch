
import cv2
import time
import os
from ultralytics import YOLO

os.environ["QT_QPA_PLATFORM"] = "xcb"
os.environ["QT_LOGGING_RULES"] = "*.debug=false;qt.qpa.*=false"

CAMERA_URL = "http://192.168.0.110:5000/stream"  # ← paste IP from streamer output

CLASS_NAMES = {0: "person", 1: "face"}
COLORS = {0: (256, 56, 56), 1: (10, 249, 72)}

def draw_detection(frame, box, class_id: int, conf: float):
    x1, y1, x2, y2 = map(int, box)
    color = COLORS.get(class_id, (255, 255, 255))
    label = CLASS_NAMES.get(class_id, str(class_id))
    caption = f"{label} {conf:.2f}"
    
    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
    (tw, th), baseline = cv2.getTextSize(caption, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
    cv2.rectangle(frame, (x1, y1 - th - 10), (x1 + tw, y1), color, -1)
    cv2.putText(frame, caption, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

def connect_camera(url, retries=5):
    """Keeps retrying until camera stream is available."""
    for i in range(retries):
        cap = cv2.VideoCapture(url)
        if cap.isOpened():
            print(f"[Server] Connected to camera stream")
            return cap
        print(f"[Server] Attempt {i+1} failed, retrying...")
        time.sleep(2)
    raise ConnectionError("Could not connect to camera")

# Load YOLO model
model_path = "/home/ankan/projects/frost/exp-3.pt"
model = YOLO(model_path).to('cuda')
device_name = model.device.type.upper()

cap = connect_camera(CAMERA_URL)

prev_time = time.time()

while True:
    ret, frame = cap.read()

    if not ret:
        print("[Server] Frame drop — reconnecting...")
        cap.release()
        cap = connect_camera(CAMERA_URL)
        continue

    # ── Hand off to your AI model ──────────────────────────
    results = model.predict(frame, conf=0.25, verbose=False, device='cuda', imgsz=320)[0]
    
    for box_obj in results.boxes:
        cls_id = int(box_obj.cls[0])
        if cls_id in CLASS_NAMES:
            draw_detection(frame, box_obj.xyxy[0].tolist(), cls_id, float(box_obj.conf[0]))
    
    # Performance Metrics
    curr_time = time.time()
    fps = 1 / (curr_time - prev_time)
    prev_time = curr_time
    
    # UI Overlay
    cv2.putText(frame, f"FPS: {fps:.1f} | Device: {device_name}", (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    # ──────────────────────────────────────────────────────

    # Dev preview — remove in production
    cv2.imshow("Server view (YOLO Inference)", frame)
    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()