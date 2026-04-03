import speech_recognition as sr
import pyttsx3
import os
from typing import Optional
import asyncio

class AudioProcessor:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.tts_engine = pyttsx3.init()
        
        # Configure TTS
        voices = self.tts_engine.getProperty('voices')
        if voices:
            self.tts_engine.setProperty('voice', voices[0].id)
        self.tts_engine.setProperty('rate', 150)
        self.tts_engine.setProperty('volume', 0.9)
    
    async def process_audio_file(self, audio_path: str) -> str:
        """Convert audio file to text"""
        try:
            with sr.AudioFile(audio_path) as source:
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source)
                audio = self.recognizer.record(source)
                
                # Try Google Speech Recognition first
                try:
                    text = self.recognizer.recognize_google(audio)
                    return text
                except sr.UnknownValueError:
                    # Fallback to Sphinx
                    try:
                        text = self.recognizer.recognize_sphinx(audio)
                        return text
                    except sr.UnknownValueError:
                        return "Unable to transcribe audio. Please speak clearly."
                        
        except Exception as e:
            print(f"Error processing audio: {e}")
            return "Error processing audio file."
    
    def speak_text(self, text: str) -> None:
        """Convert text to speech"""
        try:
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        except Exception as e:
            print(f"Error in text-to-speech: {e}")
    
    def analyze_speech_patterns(self, text: str) -> dict:
        """Analyze speech for hesitations and filler words"""
        filler_words = ['um', 'uh', 'like', 'you know', 'actually', 'basically', 'literally']
        hesitation_patterns = ['...', '---', '—']
        
        words = text.lower().split()
        hesitation_count = 0
        filler_count = 0
        found_fillers = []
        
        for word in words:
            # Clean punctuation
            clean_word = re.sub(r'[^\w\s]', '', word)
            
            if clean_word in filler_words:
                filler_count += 1
                if clean_word not in found_fillers:
                    found_fillers.append(clean_word)
            
            # Check for hesitation patterns
            for pattern in hesitation_patterns:
                if pattern in word:
                    hesitation_count += 1
        
        return {
            'filler_word_count': filler_count,
            'hesitation_count': hesitation_count,
            'found_fillers': found_fillers,
            'total_words': len(words),
            'speech_rate': len(words) / max(1, len(text.split()))  # Simple rate calculation
        }

# Global instance
audio_processor = AudioProcessor()

async def process_audio_file(audio_path: str) -> str:
    return await audio_processor.process_audio_file(audio_path)

def speak_text(text: str) -> None:
    audio_processor.speak_text(text)

def analyze_speech_patterns(text: str) -> dict:
    return audio_processor.analyze_speech_patterns(text)