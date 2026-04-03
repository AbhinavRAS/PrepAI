import random
import re
from typing import Dict, List, Optional
from datetime import datetime

class MockEvaluationService:
    def __init__(self):
        pass
    
    async def evaluate_answer(self, question: Dict, answer: str, code: Optional[str] = None) -> Dict:
        """Mock evaluation of an answer"""
        try:
            # Simulate evaluation with realistic scoring
            score = random.randint(60, 95)
            
            # Analyze answer quality
            answer_length = len(answer.split())
            word_count = len(answer.split())
            
            # Adjust score based on answer characteristics
            if answer_length < 10:
                score -= 10  # Too short
            elif answer_length > 200:
                score -= 5   # Too long
            
            # Check for filler words
            filler_words = ['um', 'uh', 'like', 'you know', 'actually', 'basically']
            filler_count = sum(1 for word in answer.lower().split() if word in filler_words)
            if filler_count > 3:
                score -= 10  # Too many fillers
            
            # Check for confidence indicators
            if any(word in answer.lower() for word in ['i think', 'maybe', 'probably']):
                score -= 5
            
            score = max(40, min(100, score))
            
            # Generate feedback
            feedback = []
            if score >= 85:
                feedback.append("Excellent answer! Clear, concise, and well-structured.")
            elif score >= 70:
                feedback.append("Good answer with minor areas for improvement.")
            elif score >= 55:
                feedback.append("Adequate answer but could be more detailed.")
            else:
                feedback.append("Answer needs significant improvement.")
            
            if filler_count > 0:
                feedback.append(f"Try to reduce filler words (used {filler_count} times).")
            
            return {
                "score": score,
                "feedback": " ".join(feedback),
                "strengths": ["Clear communication", "Relevant content"] if score >= 70 else [],
                "weaknesses": ["Needs more detail", "Reduce filler words"] if score < 70 else [],
                "suggestions": ["Be more specific", "Structure your answer better"] if score < 70 else [],
                "hesitation_count": filler_count,
                "filler_words": [word for word in answer.lower().split() if word in filler_words]
            }
            
        except Exception as e:
            print(f"Error in mock evaluation: {e}")
            return {
                "score": 50,
                "feedback": "Unable to evaluate answer due to technical issues.",
                "strengths": [],
                "weaknesses": ["Evaluation system error"],
                "suggestions": ["Please try again"],
                "hesitation_count": 0,
                "filler_words": []
            }
    
    async def complete_evaluation(self, answers: List[Dict], interview_type: str, rounds: List[str], body_language_analysis: Optional[Dict] = None) -> Dict:
        """Complete mock evaluation for all answers"""
        try:
            # Calculate overall scores
            all_scores = []
            all_strengths = []
            all_weaknesses = []
            
            for answer in answers:
                # Get mock evaluation for each answer
                eval_result = await self.evaluate_answer(
                    question={'question': answer['question'], 'type': 'general'},
                    answer=answer['answer']
                )
                
                all_scores.append(eval_result['score'])
                all_strengths.extend(eval_result.get('strengths', []))
                all_weaknesses.extend(eval_result.get('weaknesses', []))
            
            # Calculate overall score
            overall_score = sum(all_scores) / len(all_scores) if all_scores else 50
            
            # Calculate skill-specific scores
            skill_scores = {
                'communication_skills': min(100, overall_score + random.randint(-5, 10)),
                'technical_skills': min(100, overall_score + random.randint(-10, 15)),
                'confidence': min(100, overall_score + random.randint(-8, 8)),
                'clarity': min(100, overall_score + random.randint(-3, 7)),
                'problem_solving': min(100, overall_score + random.randint(-7, 12))
            }
            
            # Add body language if available
            if body_language_analysis:
                skill_scores['body_language'] = body_language_analysis.get('score', 70)
            
            # Generate recommendations
            recommendations = []
            if overall_score < 60:
                recommendations.extend([
                    "Practice speaking more clearly and confidently",
                    "Structure your answers using the STAR method",
                    "Work on reducing filler words"
                ])
            elif overall_score < 80:
                recommendations.extend([
                    "Be more specific in your answers",
                    "Provide more detailed examples"
                ])
            
            # Generate detailed feedback
            detailed_feedback = []
            for i, answer in enumerate(answers):
                eval_result = await self.evaluate_answer(
                    question={'question': answer['question'], 'type': 'general'},
                    answer=answer['answer']
                )
                
                detailed_feedback.append({
                    'question': answer['question'],
                    'user_answer': answer['answer'],
                    'feedback': eval_result['feedback'],
                    'score': eval_result['score'],
                    'hesitation_count': eval_result.get('hesitation_count', 0),
                    'filler_words': eval_result.get('filler_words', [])
                })
            
            return {
                'overall_score': round(overall_score, 1),
                'skill_scores': {k: round(v, 1) for k, v in skill_scores.items()},
                'strengths': list(set(all_strengths))[:5],
                'weaknesses': list(set(all_weaknesses))[:5],
                'detailed_feedback': detailed_feedback,
                'recommendations': recommendations[:6],
                'body_language_analysis': body_language_analysis,
                'evaluation_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error in mock evaluation: {e}")
            return {
                'overall_score': 50,
                'skill_scores': {
                    'communication_skills': 50,
                    'technical_skills': 50,
                    'confidence': 50,
                    'clarity': 50,
                    'problem_solving': 50
                },
                'strengths': ['Unable to complete evaluation'],
                'weaknesses': ['Evaluation system error'],
                'detailed_feedback': [],
                'recommendations': ['Please try again'],
                'body_language_analysis': None,
                'evaluation_date': datetime.now().isoformat()
            }

# Global instance
mock_evaluation_service = MockEvaluationService()

async def evaluate_answer(question: Dict, answer: str, code: Optional[str] = None) -> Dict:
    return await mock_evaluation_service.evaluate_answer(question, answer, code)

async def complete_evaluation(answers: List[Dict], interview_type: str, rounds: List[str], body_language_analysis: Optional[Dict] = None) -> Dict:
    return await mock_evaluation_service.complete_evaluation(answers, interview_type, rounds, body_language_analysis)