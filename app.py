import os
import shutil
import uuid
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from detector import detect_image, detect_video
from report import save_report, get_history

app = FastAPI(title="VisionTrace AI v2.0", version="2.0")

folders = ["uploads", "reports", "graphs", "static", "templates"]
for folder in folders:
    Path(folder).mkdir(parents=True, exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def welcome(request: Request):
    return templates.TemplateResponse("welcome.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/health")
async def health():
    return {"status": "running", "project": "VisionTrace AI", "version": "2.0"}

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/jpg", "image/png"}

@app.post("/upload/image")
async def upload_image(file: UploadFile = File(...)):
    try:
        if file.content_type not in ALLOWED_IMAGE_TYPES:
            return JSONResponse(status_code=400, content={"success": False, "error": "Only JPG and PNG images are allowed."})

        filename = f"image_{uuid.uuid4().hex}{os.path.splitext(file.filename)[1]}"
        save_path = os.path.join("uploads", filename)

        with open(save_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        result = detect_image(save_path)
        if not result.get("success"):
            return JSONResponse(status_code=500, content=result)

        save_report("Image", result["total_vehicles"], result["processing_time"], result["avg_confidence"])
        return JSONResponse(content=result)
    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

ALLOWED_VIDEO_TYPES = {"video/mp4", "video/x-matroska", "video/quicktime"}

@app.post("/upload/video")
async def upload_video(file: UploadFile = File(...)):
    try:
        if file.content_type not in ALLOWED_VIDEO_TYPES:
            return JSONResponse(status_code=400, content={"success": False, "error": "Only MP4, MKV and MOV videos are supported."})

        filename = f"{uuid.uuid4().hex}{os.path.splitext(file.filename)[1]}"
        save_path = os.path.join("uploads", filename)

        with open(save_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        result = detect_video(save_path)
        if not result.get("success"):
            return JSONResponse(status_code=500, content=result)

        save_report("Video", result["total_vehicles"], result["processing_time"], 0)
        return JSONResponse(content=result)
    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

@app.get("/api/history")
async def get_history_api():
    try:
        history = get_history()
        return {"success": True, "count": len(history), "data": history}
    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "error": str(e), "data": []})

if __name__ == "__main__":
    import uvicorn
    print("=" * 50)
    print(" VisionTrace AI v2.0 Started Successfully ")
    print("=" * 50)
    print("Welcome Page : http://127.0.0.1:5000")
    print("Dashboard : http://127.0.0.1:5000/dashboard")
    print("=" * 50)
    uvicorn.run("app:app", host="0.0.0.0", port=5000, reload=True)