from ultralytics import YOLO
from torch import cuda
import os
model_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'exp-3.pt'))
model = YOLO(model_path)
model.to('cuda' if cuda.is_available() else 'cpu')


def predict(frame):
    results = model.predict(frame, conf=0.25, verbose=False, device='cuda', imgsz=320)[0]
    return results
