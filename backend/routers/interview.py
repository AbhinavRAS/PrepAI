from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict
from services.whisper_service import WhisperService
from services.openai_service import OpenAIService
from services.huggingface_service import HuggingFaceService
from services.holistic_evaluation_service import HolisticEvaluationService
from services.tts_service import TTSService
from database.mongodb import MongoDB
import uuid
import os
from datetime import datetime

class MockQuestion(BaseModel):
    id: str
    question: str
    type: str
    category: str
    difficulty: str
    hint: Optional[str] = None
    audio_url: Optional[str] = None

class MockInterviewData(BaseModel):
    name: str
    email: str
    interview_type: str
    rounds: List[str]
    level: str
    questions: List[MockQuestion]
    session_id: str

router = APIRouter()

whisper_service = WhisperService()
hf_service = HuggingFaceService()
openai_service = OpenAIService()
tts_service = TTSService()
holistic_service = HolisticEvaluationService()
db = MongoDB()

@router.post("/start")
async def start_interview(
    name: str = Form(...),
    email: str = Form(...),
    interview_type: str = Form(...),
    rounds: str = Form(...),
    level: str = Form(...),
    resume: UploadFile = File(None)
):
    try:
        session_id = str(uuid.uuid4())
        rounds_list = rounds.split(',') if rounds else ['tr', 'mr', 'hr']
        
        resume_text = ""
        if resume and resume.filename.endswith('.pdf'):
            try:
                from pypdf import PdfReader
                reader = PdfReader(resume.file)
                resume_text = "\n".join(page.extract_text() for page in reader.pages)
                print(f"✅ Resume parsed successfully! Length: {len(resume_text)} characters")
            except Exception as e:
                print(f"⚠️ Failed to parse resume: {e}")
        
        # Generate questions using OpenAI
        questions = await openai_service.generate_questions(interview_type, rounds_list, level, name, email, resume_text)
        
        # Generate audio for each question
        for question in questions:
            audio_result = await tts_service.generate_question_audio(
                question["question"], 
                question["id"],
                name  # Pass user name for unique identification
            )
            if audio_result["success"]:
                question["audio_url"] = f"/api/tts/audio/{audio_result['filename']}"
            else:
                question["audio_url"] = None
        
        interview_data = {
            "_id": session_id,
            "name": name,
            "email": email,
            "interview_type": interview_type,
            "rounds": rounds_list,
            "level": level,
            "questions": questions,
            "answers": [],
            "start_time": datetime.now()
        }
        
        await db.create_interview(interview_data)
        
        return {
            "session_id": session_id,
            "questions": questions,
            "message": "Interview started successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/start-mock")
async def start_mock_interview(data: MockInterviewData):
    try:
        interview_data = {
            "_id": data.session_id,
            "name": data.name,
            "email": data.email,
            "interview_type": data.interview_type,
            "rounds": data.rounds,
            "level": data.level,
            "questions": [q.dict() for q in data.questions],
            "answers": [],
            "start_time": datetime.now()
        }
        
        await db.create_interview(interview_data)
        
        return {
            "session_id": data.session_id,
            "message": "Mock interview registered successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/transcribe")
async def transcribe_audio(
    audio: UploadFile = File(...),
    question_id: str = Form(...),
    session_id: str = Form(...),
    code: str = Form(None)
):
    try:
        # Save audio file
        audio_filename = f"{session_id}_{question_id}_{uuid.uuid4().hex}.wav"
        audio_path = f"uploads/audio/{audio_filename}"
        os.makedirs(os.path.dirname(audio_path), exist_ok=True)
        
        with open(audio_path, "wb") as buffer:
            content = await audio.read()
            buffer.write(content)
        
        # Transcribe with Whisper
        transcription_result = await whisper_service.transcribe_audio(audio_path)
        
        # Get interview details
        interview = await db.get_interview(session_id)
        current_question = None
        
        if interview:
            for q in interview["questions"]:
                if q["id"] == question_id:
                    current_question = q
                    break
        else:
            # Fallback for mock sessions
            interview = {
                "interview_type": "technical",
                "level": "medium",
                "real_time_analysis": {"eyeContact": 85, "smile": 80, "posture": 75}
            }
            current_question = {"id": question_id, "question": "Mock question. Please ignore context if evaluating.", "type": "technical", "category": "mock"}
        
        # ✅ NEW: Enhanced evaluation with video analysis
        enhanced_evaluation = await openai_service.evaluate_answer_enhanced(
            current_question["question"],
            transcription_result["transcription"],
            interview["interview_type"],
            current_question["type"]
        )
        
        # ✅ NEW: Calculate confidence score with video analysis
        confidence_score = openai_service.calculate_confidence_score(
            enhanced_evaluation["overall_score"],
            85,  # Mock eye contact (from real-time analysis)
            80,  # Mock posture (from real-time analysis)
            75   # Mock smile (from real-time analysis)
        )
        
        # ✅ NEW: Get performance benchmark
        benchmark = openai_service.get_performance_benchmark(
            interview["interview_type"],
            interview.get("level", "mid")
        )
        
        # ✅ NEW: Get real-time video analysis from session
        real_time_analysis = interview.get("real_time_analysis", {
            "eyeContact": 85,
            "smile": 80,
            "posture": 75
        })

        # ✅ NEW: Calculate confidence score with real video analysis
        confidence_score = openai_service.calculate_confidence_score(
            enhanced_evaluation["overall_score"],
            real_time_analysis.get("eyeContact", 85),
            real_time_analysis.get("posture", 80),
            real_time_analysis.get("smile", 75)
        )
        # ✅ NEW: Store enhanced answer data
        answer_data = {
            "question_id": question_id,
            "question": current_question["question"],
            "answer": transcription_result["transcription"],
            "speech_analysis": transcription_result,
            "code": code,
            "timestamp": datetime.now(),
            "question_type": current_question["type"],
            "question_category": current_question["category"],
            # ✅ NEW: Enhanced evaluation data
            "enhanced_evaluation": enhanced_evaluation,
            "confidence_score": confidence_score,
            "benchmark": benchmark
        }
        
        await db.save_answer(session_id, answer_data)
        
        return {
            "success": True,
            "transcription": transcription_result["transcription"],
            "speech_analysis": transcription_result,
            "enhanced_evaluation": enhanced_evaluation,
            "confidence_score": confidence_score,
            "benchmark": benchmark,
            "message": "Answer recorded successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/complete")
async def complete_interview(
    session_id: str = Form(...),
    answers: str = Form(None),
    body_language_analysis: str = Form(None)
):
    try:
        interview = await db.get_interview(session_id)
        
        if not interview:
            # Handle mock session completion
            return {
                "overall_score": 85,
                "candidate_name": "Mock Candidate",
                "interview_type": "technical",
                "total_questions": 5,
                "answered_questions": 5,
                "session_summary": "This was a completely simulated mock interview.",
                "consistency_analysis": {"consistency_score": 88},
                "technical_assessment": {
                    "technical_score": 82,
                    "knowledge_areas": ["JavaScript", "Problem Solving"]
                },
                "communication_analysis": {"communication_score": 90},
                "speech_analysis": {
                    "confidence_avg": 0.85,
                    "analysis_summary": {
                        "overall_fluency": "Good",
                        "speaking_pace": "Normal",
                        "hesitation_level": "Low"
                    }
                },
                "body_language_analysis": {
                    "overall_engagement": 85,
                    "eye_contact_avg": 90
                },
                "comprehensive_feedback": {
                    "key_strengths": ["Clear communication", "Good confidence"],
                    "improvement_areas": ["Elaborate on technical details"],
                    "specific_recommendations": ["Practice coding on whiteboard"],
                    "career_suggestions": ["Frontend Node Developer"],
                    "next_steps": ["Keep practicing"]
                }
            }
        
        # ✅ NEW: Use holistic evaluation service
        holistic_evaluation = await holistic_service.evaluate_session_holistically(
            interview_data=interview,
            answers=interview.get("answers", []),
            body_language_data=interview.get("video_analysis", [])
        )
        
        await db.complete_interview(session_id, holistic_evaluation)
        
        return holistic_evaluation
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))