import cv2
import time
import os
from ultralytics import YOLO
import torch
import threading

CAMERA_URL = "http://192.168.0.110:5001/stream"

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

def redaction(frame, box, class_id = 1, conf = 0.5):
    x1, y1, x2, y2 = map(int, box)
    h, w = frame.shape[:2]
    x1b, y1b = max(0, x1-10), max(0, y1-10)
    x2b, y2b = min(w, x2+10), min(h, y2+10)
    roi = frame[y1b:y2b, x1b:x2b]
    blurred_roi = cv2.blur(roi, (25, 25))
    frame[y1b:y2b, x1b:x2b] = blurred_roi

def connect_camera(url, retries=2, timeout=5):
    for i in range(retries):
        result = {}
        def _open():
            try:
                cap = cv2.VideoCapture(url)
                if cap.isOpened():
                    result['cap'] = cap
                else:
                    cap.release()
            except Exception:
                pass

        t = threading.Thread(target=_open, daemon=True)
        t.start()
        t.join(timeout=timeout)

        if 'cap' in result:
            print(f"[Server] Connected to camera stream")
            return result['cap']
        print(f"[Server] Attempt {i+1}/{retries} timed out for {url}")

    raise ConnectionError(f"Could not connect to camera at {url}")

if __name__ == '__main__':
    model_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../ai/exp-3.pt'))
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    model = YOLO(model_path).to(device)
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

        results = model.predict(frame, conf=0.25, verbose=False, device=device, imgsz=320)[0]
        
        for box_obj in results.boxes:
            cls_id = int(box_obj.cls[0])
            if cls_id in CLASS_NAMES:
                draw_detection(frame, box_obj.xyxy[0].tolist(), cls_id, float(box_obj.conf[0]))
        
        curr_time = time.time()
        fps = 1 / (curr_time - prev_time)
        prev_time = curr_time
        
        cv2.putText(frame, f"FPS: {fps:.1f} | Device: {device_name}", (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        cv2.imshow("Server view (YOLO Inference)", frame)
        if cv2.waitKey(1) == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()