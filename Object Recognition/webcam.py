from ultralytics import YOLO

# Load the model
model = YOLO('yolov8n.pt')

results = model.predict(source=0, show= True)