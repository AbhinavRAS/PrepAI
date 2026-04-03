import os
import sys
import io

# Force UTF-8 on Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from routers.tts import router as tts_router
import uvicorn
from datetime import datetime

from routers.interview import router as interview_router
from routers.analysis import router as analysis_router
from services.whisper_service import WhisperService
from services.huggingface_service import HuggingFaceService
from services.mediapipe_service import MediaPipeService
from database.mongodb import MongoDB

app = FastAPI(title="AI Smart Interview Agent", version="2.0")

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://127.0.0.1:8000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
whisper_service = WhisperService()
hf_service = HuggingFaceService()
mediapipe_service = MediaPipeService()
db = MongoDB()

# Include routers
app.include_router(interview_router, prefix="/api/interview")
app.include_router(analysis_router, prefix="/api/analysis")
app.include_router(tts_router, prefix="/api/tts")


# Static files for uploads
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.mount("/tts-audio", StaticFiles(directory="uploads/tts"), name="tts-audio")

import os
from fastapi.responses import FileResponse

frontend_dist = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "frontend", "dist")

if os.path.exists(frontend_dist):
    # Mount assets folder explicitly so they load efficiently
    assets_dir = os.path.join(frontend_dist, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")
        
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="API route not found")
            
        file_path = os.path.join(frontend_dist, full_path)
        if full_path and os.path.isfile(file_path):
            return FileResponse(file_path)
        index_path = os.path.join(frontend_dist, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        return {"status": "Frontend not built fully. Please view README."}
else:
    @app.get("/")
    async def root():
        return {"status": "Frontend not built yet. Please run npm run build in frontend directory."}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)