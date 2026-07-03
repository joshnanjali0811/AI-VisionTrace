import os
import time
import cv2
import numpy as np
from ultralytics import YOLO
from utils import image_to_base64, traffic_status, elapsed_time

print("Loading VisionTrace AI Model...")
model = YOLO("yolov8n.pt")
model.to('cpu')
print("YOLO Model Loaded Successfully!")

VEHICLE_CLASSES = {
    1: "bicycle",
    2: "car",
    3: "motorcycle",
    5: "bus",
    7: "truck"
}

COLORS = {
    "bicycle": (6, 182, 212),
    "car": (139, 92, 246),
    "motorcycle": (34, 197, 94),
    "bus": (59, 130, 246),
    "truck": (249, 115, 22)
}

def initialize_counts():
    return {"bicycle": 0, "car": 0, "motorcycle": 0, "bus": 0, "truck": 0}

def draw_box(frame, x1, y1, x2, y2, label, confidence):
    color = COLORS.get(label, (255, 255, 255))
    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 3)
    text = f"{label} {confidence:.0%}"
    cv2.putText(frame, text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

def detect_frame(frame):
    vehicle_counts = initialize_counts()
    total_confidence = 0
    total_detected = 0

    results = model(frame, conf=0.25, iou=0.45, imgsz=1280, verbose=False)[0]

    for box in results.boxes:
        cls = int(box.cls[0])
        if cls not in VEHICLE_CLASSES:
            continue
        label = VEHICLE_CLASSES[cls]
        confidence = float(box.conf[0])
        x1, y1, x2, y2 = map(int, box.xyxy[0])

        vehicle_counts[label] += 1
        total_detected += 1
        total_confidence += confidence
        draw_box(frame, x1, y1, x2, y2, label, confidence)

    avg_confidence = round((total_confidence / total_detected) * 100, 2) if total_detected > 0 else 0
    return frame, vehicle_counts, total_detected, avg_confidence

def detect_image(image_path):
    start_time = time.time()
    frame = cv2.imread(image_path)
    if frame is None:
        return {"success": False, "error": "Unable to read image."}

    processed_frame, vehicle_counts, total_detected, avg_confidence = detect_frame(frame)
    processing_time = elapsed_time(start_time, time.time())
    encoded_image = image_to_base64(processed_frame)

    return {
        "success": True,
        "image": encoded_image,
        "total_vehicles": total_detected,
        "vehicle_counts": vehicle_counts,
        "avg_confidence": avg_confidence,
        "processing_time": processing_time,
        "traffic_status": traffic_status(total_detected)
    }

def detect_video(video_path):
    start_time = time.time()
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return {"success": False, "error": "Unable to open video."}

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30

    output_name = f"output_{int(time.time())}.mp4"
    output_path = os.path.join("uploads", output_name)

    writer = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*"mp4v"), fps, (width, height))

    total_frames = 0
    total_vehicles = 0
    final_counts = initialize_counts()

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        total_frames += 1
        if total_frames % 3!= 0:
            writer.write(frame)
            continue

        processed_frame, counts, detected, _ = detect_frame(frame)
        writer.write(processed_frame)
        total_vehicles += detected
        for key in final_counts:
            final_counts[key] += counts[key]

    cap.release()
    writer.release()

    avg_frame = round(total_vehicles / total_frames, 2) if total_frames else 0
    processing_time = elapsed_time(start_time, time.time())

    return {
        "success": True,
        "video_url": "/" + output_path.replace("\\", "/"),
        "total_vehicles": total_vehicles,
        "vehicle_counts": final_counts,
        "avg_vehicles_per_frame": avg_frame,
        "processing_time": processing_time,
        "traffic_status": traffic_status(avg_frame)
    }