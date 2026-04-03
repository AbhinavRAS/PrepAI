from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from services.tts_service import TTSService
import os

router = APIRouter()
tts_service = TTSService()

@router.post("/generate-audio")
async def generate_audio(text: str, voice: str = "alloy"):
    """Convert text to speech"""
    try:
        result = await tts_service.generate_speech(text, voice)
        if result["success"]:
            return {
                "audio_url": f"/api/tts/audio/{result['filename']}",
                "filename": result["filename"],
                "text": result["text"]
            }
        else:
            raise HTTPException(status_code=500, detail=result["error"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/audio/{filename}")
async def get_audio_file(filename: str):
    """Serve audio files"""
    file_path = f"uploads/tts/{filename}"
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="audio/mpeg")
    else:
        raise HTTPException(status_code=404, detail="Audio file not found")

@router.post("/generate-question-audio")
async def generate_question_audio(question_text: str, question_id: str):
    """Generate audio for interview question"""
    try:
        result = await tts_service.generate_question_audio(question_text, question_id)
        if result["success"]:
            return {
                "audio_url": f"/api/tts/audio/{result['filename']}",
                "filename": result["filename"],
                "question_id": question_id,
                "text": result["text"]
            }
        else:
            raise HTTPException(status_code=500, detail=result["error"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))