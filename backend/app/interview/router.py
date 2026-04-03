from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from typing import List, Optional
import uuid
import os
from datetime import datetime

from .question_engine import generate_questions
from .evaluation_service import evaluate_answer, complete_evaluation
from .mock_evaluation_service import evaluate_answer, complete_evaluation
from .audio_processor import process_audio_file
from .video_analyzer import analyze_video
from .code_evaluator import evaluate_code

router = APIRouter()

# Store sessions in memory (in production, use Redis or database)
sessions = {}

@router.post("/start")
async def start_interview(
    name: str = Form(...),
    email: str = Form(...),
    interview_type: str = Form(...),
    rounds: str = Form(...),  # Changed from rounds: str to handle both string and array
    level: str = Form(...)
):
    try:
        session_id = str(uuid.uuid4())
        
        # Handle both string and array formats for rounds
        if isinstance(rounds, str):
            rounds_list = rounds.split(',') if rounds else ['tr', 'mr', 'hr']
        elif isinstance(rounds, list):
            rounds_list = rounds
        else:
            rounds_list = ['tr', 'mr', 'hr']
        
        questions = generate_questions(interview_type, rounds_list, level)
        
        sessions[session_id] = {
            'name': name,
            'email': email,
            'interview_type': interview_type,
            'rounds': rounds_list,  # Store as list for consistency
            'level': level,
            'questions': questions,
            'answers': [],
            'start_time': datetime.now(),
            'video_frames': []
        }
        
        return {
            "session_id": session_id,
            "questions": questions,
            "message": "Interview started successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/submit-answer")
async def submit_answer(
    audio: UploadFile = File(...),
    question_id: str = Form(...),
    session_id: str = Form(...),
    code: Optional[str] = Form(None)
):
    try:
        if session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Save audio file
        audio_filename = f"{session_id}_{question_id}_{uuid.uuid4().hex}.wav"
        audio_path = f"uploads/audio/{audio_filename}"
        os.makedirs(os.path.dirname(audio_path), exist_ok=True)
        
        with open(audio_path, "wb") as buffer:
            content = await audio.read()
            buffer.write(content)
        
        # Process audio and get transcription
        transcription = await process_audio_file(audio_path)
        
        # Find the question
        session = sessions[session_id]
        question = None
        for q in session['questions']:
            if q['id'] == question_id:
                question = q
                break
        
        if not question:
            raise HTTPException(status_code=404, detail="Question not found")
        
        # Evaluate answer if it's a coding question
        code_score = None
        code_feedback = None
        if question.get('type') == 'coding' and code:
            code_score, code_feedback = await evaluate_code(code, question.get('expected_solution'))
        
        # Store answer
        answer_data = {
            'question_id': question_id,
            'question': question['question'],
            'transcription': transcription,
            'audio_path': audio_path,
            'code': code,
            'code_score': code_score,
            'code_feedback': code_feedback,
            'timestamp': datetime.now()
        }
        
        session['answers'].append(answer_data)
        
        return {
            "transcription": transcription,
            "audio_url": f"/uploads/audio/{audio_filename}",
            "code_score": code_score,
            "code_feedback": code_feedback
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload-video-frame")
async def upload_video_frame(
    frame: UploadFile = File(...),
    session_id: str = Form(...)
):
    try:
        if session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Save frame
        frame_filename = f"{session_id}_{uuid.uuid4().hex}.jpg"
        frame_path = f"uploads/frames/{frame_filename}"
        os.makedirs(os.path.dirname(frame_path), exist_ok=True)
        
        with open(frame_path, "wb") as buffer:
            content = await frame.read()
            buffer.write(content)
        
        sessions[session_id]['video_frames'].append(frame_path)
        
        return {"status": "Frame uploaded successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/complete")
async def complete_interview(
    session_id: str = Form(...),
    answers: Optional[str] = Form(None)
):
    try:
        if session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session = sessions[session_id]
        
        # Analyze video if required
        body_language_analysis = None
        if session['interview_type'] in ['ips', 'ias'] and session['video_frames']:
            body_language_analysis = await analyze_video(session['video_frames'])
        
        # Complete evaluation
        evaluation_result = await complete_evaluation(
            session['answers'],
            session['interview_type'],
            session['rounds'],
            body_language_analysis
        )
        
        # Add session metadata
        evaluation_result['candidate_name'] = session['name']
        evaluation_result['interview_type'] = session['interview_type']
        evaluation_result['session_id'] = session_id
        evaluation_result['duration'] = str(datetime.now() - session['start_time'])
        
        # Clean up session
        del sessions[session_id]
        
        return evaluation_result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now()}