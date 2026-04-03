from sqlalchemy.orm import Session
from .models import User, Interview, Answer, CodingSubmission

def get_or_create_user(db: Session, name: str, email: str):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(name=name, email=email)
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


def create_interview(db: Session, user_id: int, interview_type, mode, level, score):
    interview = Interview(
        user_id=user_id,
        interview_type=interview_type,
        mode=mode,
        level=level,
        overall_score=score
    )
    db.add(interview)
    db.commit()
    db.refresh(interview)
    return interview


def add_answer(db, interview_id, q, a, scores):
    ans = Answer(
        interview_id=interview_id,
        question=q,
        answer=a,
        communication=scores["communication"],
        confidence=scores["confidence"],
        technical=scores["technical"],
        pronunciation=scores["pronunciation"]
    )
    db.add(ans)
    db.commit()


def add_code_submission(db, interview_id, data):
    submission = CodingSubmission(
        interview_id=interview_id,
        question=data["question"],
        code=data["code"],
        language=data["language"],
        score=data["score"],
        feedback=data["feedback"]
    )
    db.add(submission)
    db.commit()
