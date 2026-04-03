from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os

# Database URL - you can configure this in .env
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./interview.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    from app.database.models import Base
    Base.metadata.create_all(bind=engine)

def seed_questions():
    """Seed the database with initial questions"""
    from app.database.models import Question
    from app.interview.question_engine import question_engine
    
    db = SessionLocal()
    try:
        # Check if questions already exist
        if db.query(Question).count() > 0:
            return
        
        # Add questions from the question engine
        for interview_type, rounds in question_engine.question_bank.items():
            for round_type, questions in rounds.items():
                for question in questions:
                    db_question = Question(
                        question_id=question['id'],
                        question_text=question['question'],
                        interview_type=interview_type,
                        round_type=round_type,
                        category=question.get('category'),
                        difficulty=question.get('difficulty'),
                        question_type=question.get('type'),
                        expected_solution=question.get('expected_solution'),
                        hint=question.get('hint')
                    )
                    db.add(db_question)
        
        db.commit()
        print("Database seeded with questions successfully!")
        
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()