import openai
import re
from typing import Dict, List, Optional
from datetime import datetime
import json
import os
import random
from openai import AsyncOpenAI

class EvaluationService:
    def __init__(self):
        # Check if Groq API key is available and valid
        self.api_key = os.getenv('GROQ_API_KEY')
        self.openai_available = bool(self.api_key) and self.api_key.startswith('gsk_')
        self.client = AsyncOpenAI(base_url="https://api.groq.com/openai/v1", api_key=self.api_key) if self.openai_available else None
        if not self.openai_available:
            print("⚠️ API not available. Using mock evaluation service.")
    
    async def evaluate_answer(self, question: Dict, answer: str, code: Optional[str] = None) -> Dict:
        """Evaluate a single answer"""
        if self.openai_available:
            # Use OpenAI API
            return await self._evaluate_with_openai(question, answer, code)
        else:
            # Use mock service
            from .mock_evaluation_service import evaluate_answer as mock_evaluate_answer
            return await mock_evaluate_answer(question, answer, code)
    
    async def _evaluate_with_openai(self, question: Dict, answer: str, code: Optional[str] = None) -> Dict:
        """Evaluate answer using OpenAI API"""
        try:
            # Base evaluation prompt
            evaluation_prompt = f"""
            Evaluate the following answer for the given interview question. Provide detailed feedback and a score out of 100.

            Question: {question['question']}
            Question Type: {question['type']}
            Category: {question['category']}
            Difficulty: {question['difficulty']}

            Answer: {answer}

            Please evaluate on:
            1. Relevance to the question
            2. Technical accuracy (if applicable)
            3. Communication clarity
            4. Confidence level
            5. Completeness of answer

            Provide response in JSON format:
            {{
                "score": <0-100>,
                "feedback": "<detailed feedback>",
                "strengths": ["<strength1>", "<strength2>"],
                "weaknesses": ["<weakness1>", "<weakness2>"],
                "suggestions": ["<suggestion1>", "<suggestion2>"],
                "hesitation_count": <number>,
                "filler_words": ["<word1>", "<word2>"]
            }}
            """
            
            response = await self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are an expert interview evaluator."},
                    {"role": "user", "content": evaluation_prompt}
                ],
                temperature=0.3
            )
            
            evaluation = json.loads(response.choices[0].message.content)
            
            # Add code evaluation if present
            if code and question.get('type') == 'coding':
                code_eval = await self._evaluate_code_with_openai(code, question.get('expected_solution'))
                evaluation['code_score'] = code_eval['score']
                evaluation['code_feedback'] = code_eval['feedback']
            
            return evaluation
            
        except Exception as e:
            print(f"Error evaluating answer: {e}")
            return {
                "score": 50,
                "feedback": "Unable to evaluate answer due to technical issues.",
                "strengths": [],
                "weaknesses": ["Evaluation system error"],
                "suggestions": ["Please try again"],
                "hesitation_count": 0,
                "filler_words": []
            }
    
    async def _evaluate_code_with_openai(self, code: str, expected_solution: str) -> Dict:
        """Evaluate code using OpenAI API"""
        try:
            code_prompt = f"""
            Evaluate the following code solution. Compare it with the expected approach and provide feedback.

            Submitted Code:
            {code}

            Expected Solution (reference):
            {expected_solution}

            Evaluate on:
            1. Correctness
            2. Efficiency
            3. Code quality and readability
            4. Edge case handling
            5. Best practices

            Provide response in JSON format:
            {{
                "score": <0-100>,
                "feedback": "<detailed feedback>",
                "issues": ["<issue1>", "<issue2>"],
                "suggestions": ["<suggestion1>", "<suggestion2>"]
            }}
            """
            
            response = await self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are an expert code reviewer."},
                    {"role": "user", "content": code_prompt}
                ],
                temperature=0.2
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            print(f"Error evaluating code: {e}")
            return {
                "score": 50,
                "feedback": "Unable to evaluate code due to technical issues.",
                "issues": ["Evaluation system error"],
                "suggestions": ["Please try again"]
            }
    
    async def complete_evaluation(self, answers: List[Dict], interview_type: str, rounds: List[str], body_language_analysis: Optional[Dict] = None) -> Dict:
        """Complete evaluation for all answers"""
        try:
            # Evaluate each answer
            detailed_feedback = []
            all_scores = []
            all_strengths = []
            all_weaknesses = []
            
            for answer in answers:
                question = {
                    'question': answer['question'],
                    'type': 'technical',  # Default, should be stored in answer
                    'category': 'general',
                    'difficulty': 'medium'
                }
                
                evaluation = await self.evaluate_answer(question, answer['answer'], answer.get('code'))
                
                detailed_feedback.append({
                    'question': answer['question'],
                    'user_answer': answer['answer'],
                    'feedback': evaluation['feedback'],
                    'score': evaluation['score'],
                    'hesitation_count': evaluation.get('hesitation_count', 0),
                    'filler_words': evaluation.get('filler_words', [])
                })
                
                all_scores.append(evaluation['score'])
                all_strengths.extend(evaluation.get('strengths', []))
                all_weaknesses.extend(evaluation.get('weaknesses', []))
            
            # Calculate overall scores
            overall_score = sum(all_scores) / len(all_scores) if all_scores else 0
            
            # Calculate skill-specific scores
            skill_scores = {
                'communication_skills': min(100, overall_score + random.randint(-10, 10)),
                'technical_skills': min(100, overall_score + random.randint(-15, 15)),
                'confidence': min(100, overall_score + random.randint(-10, 10)),
                'clarity': min(100, overall_score + random.randint(-5, 5)),
                'problem_solving': min(100, overall_score + random.randint(-10, 12))
            }
            
            # Add body language score if available
            if body_language_analysis:
                skill_scores['body_language'] = body_language_analysis.get('score', 70)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(skill_scores, all_weaknesses)
            
            return {
                'overall_score': round(overall_score, 1),
                'skill_scores': skill_scores,
                'strengths': list(set(all_strengths))[:5],  # Top 5 unique strengths
                'weaknesses': list(set(all_weaknesses))[:5],  # Top 5 unique weaknesses
                'detailed_feedback': detailed_feedback,
                'recommendations': recommendations,
                'body_language_analysis': body_language_analysis,
                'evaluation_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error in complete evaluation: {e}")
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
    
    def _generate_recommendations(self, skill_scores: Dict, weaknesses: List[str]) -> List[str]:
        """Generate personalized recommendations"""
        recommendations = []
        
        # Based on skill scores
        for skill, score in skill_scores.items():
            if score < 60:
                if skill == 'communication_skills':
                    recommendations.append("Practice speaking clearly and concisely. Try recording yourself and reviewing.")
                elif skill == 'technical_skills':
                    recommendations.append("Focus on strengthening your technical knowledge through online courses and practice.")
                elif skill == 'confidence':
                    recommendations.append("Build confidence through mock interviews and positive self-talk.")
                elif skill == 'clarity':
                    recommendations.append("Structure your answers using the STAR method (Situation, Task, Action, Result).")
                elif skill == 'problem_solving':
                    recommendations.append("Practice solving problems systematically and explaining your thought process.")
                elif skill == 'body_language':
                    recommendations.append("Work on maintaining good posture, eye contact, and appropriate hand gestures.")
        
        # Based on specific weaknesses
        for weakness in weaknesses:
            if 'hesitation' in weakness.lower():
                recommendations.append("Practice reducing filler words by taking brief pauses instead of using 'um' or 'uh'.")
            if 'technical' in weakness.lower():
                recommendations.append("Review fundamental concepts and stay updated with industry trends.")
        
        return recommendations[:6]  # Return top 6 recommendations

# Global instance
evaluation_service = EvaluationService()

async def evaluate_answer(question: Dict, answer: str, code: Optional[str] = None) -> Dict:
    return await evaluation_service.evaluate_answer(question, answer, code)

async def complete_evaluation(answers: List[Dict], interview_type: str, rounds: List[str], body_language_analysis: Optional[Dict] = None) -> Dict:
    return await evaluation_service.complete_evaluation(answers, interview_type, rounds, body_language_analysis)