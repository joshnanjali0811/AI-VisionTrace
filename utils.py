import os
import base64
import uuid
from datetime import datetime
from PIL import Image
import cv2

UPLOAD_FOLDER = "uploads"
GRAPH_FOLDER = "graphs"
REPORT_FOLDER = "reports"

ALLOWED_IMAGE = {"jpg", "jpeg", "png"}
ALLOWED_VIDEO = {"mp4"}

MAX_FILE_SIZE = 500 * 1024 * 1024

def create_folders():
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(GRAPH_FOLDER, exist_ok=True)
    os.makedirs(REPORT_FOLDER, exist_ok=True)

def allowed_image(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_IMAGE

def allowed_video(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_VIDEO

def unique_filename(filename):
    extension = filename.rsplit(".", 1)[1]
    unique = f"{uuid.uuid4().hex}.{extension}"
    return unique

def save_upload(file):
    filename = unique_filename(file.filename)
    path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(path)
    return path

def image_to_base64(image):
    _, buffer = cv2.imencode(".jpg", image)
    encoded = base64.b64encode(buffer)
    return encoded.decode("utf-8")

def current_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def file_size(file):
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)
    return size

def validate_upload(file):
    if file.filename == "":
        return False, "No file selected."
    if file_size(file) > MAX_FILE_SIZE:
        return False, "File size exceeds 500MB."
    return True, ""

def traffic_status(total):
    if total <= 15:
        return "Low"
    elif total <= 35:
        return "Normal"
    elif total <= 60:
        return "Heavy"
    else:
        return "Very Heavy"

def safe_round(value):
    try:
        return round(float(value), 2)
    except:
        return 0

def elapsed_time(start, end):
    return round(end - start, 2)