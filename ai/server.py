from ultralytics import YOLO
from torch import cuda
model = YOLO("/home/ankan/projects/frost/exp-3.pt")
model.to('cuda' if cuda.is_available() else 'cpu')


def predict(frame):
    results = model.predict(frame, conf=0.25, verbose=False, device='cuda', imgsz=320)[0]
    return results
