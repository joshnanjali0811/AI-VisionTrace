import os
import pandas as pd
from datetime import datetime

REPORT_FOLDER = "reports"
REPORT_FILE = os.path.join(REPORT_FOLDER, "history.csv")

def initialize_report():
    os.makedirs(REPORT_FOLDER, exist_ok=True)
    if not os.path.exists(REPORT_FILE):
        df = pd.DataFrame(columns=["Timestamp", "Type", "Total Vehicles", "Processing Time", "Average Confidence"])
        df.to_csv(REPORT_FILE, index=False)

def save_report(file_type, total_vehicles, processing_time, avg_confidence):
    initialize_report()
    row = {
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Type": file_type,
        "Total Vehicles": total_vehicles,
        "Processing Time": processing_time,
        "Average Confidence": avg_confidence
    }
    df = pd.read_csv(REPORT_FILE)
    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    df.to_csv(REPORT_FILE, index=False)

def get_history():
    initialize_report()
    df = pd.read_csv(REPORT_FILE)
    return df.to_dict(orient="records")

def history_json():
    return {"success": True, "data": get_history()}