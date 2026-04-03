from sqlalchemy import Column, Integer, String, DateTime, Float, Text, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    interviews = relationship("Interview", back_populates="user")

class Interview(Base):
    __tablename__ = "interviews"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    interview_type = Column(String, nullable=False)
    rounds = Column(Text)  # JSON string
    level = Column(String)
    status = Column(String, default="started")  # started, completed, cancelled
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime)
    overall_score = Column(Float)
    
    user = relationship("User", back_populates="interviews")
    answers = relationship("Answer", back_populates="interview")
    evaluation = relationship("Evaluation", back_populates="interview", uselist=False)

class Answer(Base):
    __tablename__ = "answers"
    
    id = Column(Integer, primary_key=True, index=True)
    interview_id = Column(Integer, ForeignKey("interviews.id"))
    question_id = Column(String, nullable=False)
    question_text = Column(Text, nullable=False)
    answer_text = Column(Text)
    audio_path = Column(String)
    code = Column(Text)
    code_score = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    interview = relationship("Interview", back_populates="answers")

class Evaluation(Base):
    __tablename__ = "evaluations"
    
    id = Column(Integer, primary_key=True, index=True)
    interview_id = Column(Integer, ForeignKey("interviews.id"), unique=True)
    overall_score = Column(Float)
    skill_scores = Column(Text)  # JSON string
    strengths = Column(Text)  # JSON array
    weaknesses = Column(Text)  # JSON array
    recommendations = Column(Text)  # JSON array
    detailed_feedback = Column(Text)  # JSON string
    body_language_analysis = Column(Text)  # JSON string
    created_at = Column(DateTime, default=datetime.utcnow)
    
    interview = relationship("Interview", back_populates="evaluation")

class Question(Base):
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(String, unique=True, nullable=False, index=True)
    question_text = Column(Text, nullable=False)
    interview_type = Column(String, nullable=False)
    round_type = Column(String, nullable=False)
    category = Column(String)
    difficulty = Column(String)
    question_type = Column(String)  # technical, behavioral, personal, coding, situational
    expected_solution = Column(Text)
    hint = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)