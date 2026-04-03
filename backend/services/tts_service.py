import edge_tts
import os
import uuid
from datetime import datetime
from typing import Dict

class TTSService:
    def __init__(self):
        pass
    
    async def generate_speech(self, text: str, voice: str = "en-US-AriaNeural", user_name: str = None, question_id: str = None) -> Dict:
        """Convert text to speech using Edge TTS with user-based naming"""
        try:
            # Create user-specific filename
            user_prefix = user_name.replace(" ", "_").lower() if user_name else "user"
            question_prefix = question_id if question_id else uuid.uuid4().hex[:8]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{user_prefix}_{question_prefix}_{timestamp}.mp3"
            filepath = f"uploads/tts/{filename}"
            
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(filepath)
            
            return {
                "success": True,
                "filename": filename,
                "filepath": filepath,
                "text": text,
                "user_name": user_name,
                "question_id": question_id,
                "timestamp": timestamp
            }
            
        except Exception as e:
            print(f"⚠️ TTS generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "text": text
            }
    
    async def generate_question_audio(self, question_text: str, question_id: str, user_name: str = None) -> Dict:
        """Generate audio for a specific question with user identification"""
        return await self.generate_speech(question_text, "en-US-AriaNeural", user_name, question_id)