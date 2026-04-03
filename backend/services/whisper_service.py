import whisper
import torch
import numpy as np
from typing import Dict, List
import asyncio
import re
import json
import time
import random

class WhisperService:
    def __init__(self):
        try:
            self.model = whisper.load_model("base")
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            self.mock_mode = False
        except Exception as e:
            print(f"⚠️ Whisper model loading failed: {e}")
            print("🔄 Using mock transcription service")
            self.mock_mode = True
        
    async def transcribe_audio(self, audio_path: str) -> Dict:
        """Transcribe audio and analyze speech patterns"""
        if self.mock_mode:
            # Mock transcription for testing
            await asyncio.sleep(1)  # Simulate processing time
            return {
                "transcription": "This is a mock transcription for testing purposes.",
                "confidence": random.uniform(0.7, 0.95),
                "hesitations": random.randint(0, 3),
                "filler_words": random.randint(1, 5),
                "speech_rate": random.uniform(120, 180),
                "word_timestamps": []
            }
        
        # Real Whisper processing
        result = self.model.transcribe(audio_path, word_timestamps=True)
        analysis = self._analyze_speech_patterns(result)
        return {
            "transcription": result["text"],
            "confidence": self._calculate_confidence(result),
            "hesitations": analysis["hesitations"],
            "filler_words": analysis["filler_words"],
            "speech_rate": analysis["speech_rate"],
            "word_timestamps": result.get("word_timestamps", [])
        }

    def _analyze_speech_patterns(self, result: Dict) -> Dict:
        """Analyze transcription for hesitations and speech rate"""
        text = result.get("text", "")
        hesitation_words = ["um", "uh", "ah", "like", "you know"]
        words = text.lower().split()
        filler_words = sum(1 for word in words if word in hesitation_words)
        hesitations = filler_words // 2  # arbitrary estimate
        
        segments = result.get("segments", [])
        duration = 0
        if segments:
            duration = segments[-1].get("end", 0) - segments[0].get("start", 0)
        
        speech_rate = 150
        if duration > 0 and len(words) > 0:
            minutes = max(duration / 60.0, 0.1)
            speech_rate = len(words) / minutes
            
        return {
            "hesitations": hesitations,
            "filler_words": filler_words,
            "speech_rate": min(max(speech_rate, 80), 250)
        }

    def _calculate_confidence(self, result: Dict) -> float:
        """Calculate confidence score from transcription result"""
        segments = result.get("segments", [])
        if not segments:
            return 0.8
        
        logprobs = [s.get("avg_logprob", -1.0) for s in segments]
        avg_logprob = sum(logprobs) / len(logprobs) if logprobs else -1.0
        confidence = max(0.0, min(1.0, np.exp(avg_logprob)))
        
        return confidence