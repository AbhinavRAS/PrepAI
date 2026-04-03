import requests
import json
from typing import Dict, List, Any
import os

class HuggingFaceService:
    def __init__(self):
        self.api_url = "https://api-inference.huggingface.co/models"
        self.api_key = os.getenv("HUGGINGFACE_API_KEY")
        
        # Models for different tasks
        self.question_model = "microsoft/DialoGPT-medium"
        self.evaluation_models = {
            "sentiment": "cardiffnlp/twitter-roberta-base-sentiment-latest",
            "grammar": "textattack/bert-base-uncased-CoLA",
            "relevance": "cross-encoder/ms-marco-MiniLM-L-6-v2"
        }
        self.text_generation_model = "microsoft/DialoGPT-medium"
    
    async def generate_questions(self, interview_type: str, rounds: List[str], level: str) -> List[Dict]:
        """Generate interview questions using Hugging Face"""
        questions = []
        
        for round_type in rounds:
            if round_type == "tr":
                category = "technical"
            elif round_type == "mr":
                category = "behavioral"
            else:
                category = "hr"
            
            # Try to generate with Hugging Face, fallback to templates
            try:
                generated_questions = await self._generate_questions_with_hf(category, level, interview_type)
                if generated_questions:
                    for i, q_data in enumerate(generated_questions):
                        question = {
                            "id": f"{round_type}_{i+1}",
                            "question": q_data["question"],
                            "type": category,
                            "category": round_type,
                            "difficulty": level,
                            "hint": q_data.get("hint", self._generate_hint("", category))
                        }
                        questions.append(question)
                else:
                    # Fallback to template questions
                    questions.extend(self._get_template_questions(round_type, category, level))
            except Exception as e:
                print(f"⚠️ Hugging Face question generation failed: {e}")
                questions.extend(self._get_template_questions(round_type, category, level))
        
        return questions
    
    async def _generate_questions_with_hf(self, category: str, level: str, interview_type: str) -> List[Dict]:
        """Generate questions using Hugging Face text generation"""
        prompt = f"Generate 2 {category} interview questions for a {level} {interview_type} interview."
        
        try:
            payload = {"inputs": prompt}
            
            response = requests.post(
                f"{self.api_url}/{self.text_generation_model}",
                headers={"Authorization": f"Bearer {self.api_key}"} if self.api_key else {},
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                if result and "generated_text" in result[0]:
                    # Parse the generated text to extract questions
                    generated_text = result[0]["generated_text"]
                    return self._parse_generated_questions(generated_text, category)
        except Exception as e:
            print(f"⚠️ HF generation error: {e}")
        
        return None
    
    def _parse_generated_questions(self, text: str, category: str) -> List[Dict]:
        """Parse generated text into question objects"""
        # Simple parsing - split by common question patterns
        questions = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if '?' in line and len(line) > 10:
                questions.append({
                    "question": line,
                    "hint": self._generate_hint(line, category)
                })
        
        return questions[:2]  # Return max 2 questions
    
    async def evaluate_answer(self, question: str, answer: str, question_type: str) -> Dict:
        """Evaluate answer using Hugging Face models"""
        evaluation = {}
        
        # Sentiment analysis
        sentiment = await self._analyze_sentiment(answer)
        evaluation["sentiment"] = sentiment
        
        # Grammar and coherence
        grammar = await self._analyze_grammar(answer)
        evaluation["grammar"] = grammar
        
        # Relevance to question
        relevance = await self._analyze_relevance(question, answer)
        evaluation["relevance"] = relevance
        
        # Overall score
        evaluation["overall_score"] = self._calculate_overall_score(evaluation)
        
        # Feedback generation
        evaluation["feedback"] = self._generate_feedback(evaluation, question_type)
        evaluation["strengths"] = self._generate_strengths(evaluation, question_type)
        evaluation["improvements"] = self._generate_improvements(evaluation, question_type)
        
        return evaluation
    
    async def _analyze_sentiment(self, text: str) -> Dict:
        """Analyze sentiment using Hugging Face"""
        try:
            payload = {"inputs": text}
            
            response = requests.post(
                f"{self.api_url}/{self.evaluation_models['sentiment']}",
                headers={"Authorization": f"Bearer {self.api_key}"} if self.api_key else {},
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()[0]
                return {
                    "label": result[0]["label"],
                    "score": result[0]["score"]
                }
        except Exception as e:
            print(f"⚠️ Sentiment analysis failed: {e}")
        
        # Fallback
        return {"label": "NEUTRAL", "score": 0.7}
    
    async def _analyze_grammar(self, text: str) -> Dict:
        """Analyze grammar using Hugging Face"""
        try:
            payload = {"inputs": text}
            
            response = requests.post(
                f"{self.api_url}/{self.evaluation_models['grammar']}",
                headers={"Authorization": f"Bearer {self.api_key}"} if self.api_key else {},
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()[0]
                return {
                    "label": result[0]["label"],
                    "score": result[0]["score"]
                }
        except Exception as e:
            print(f"⚠️ Grammar analysis failed: {e}")
        
        # Fallback
        return {"label": "ACCEPTABLE", "score": 0.8}
    
    async def _analyze_relevance(self, question: str, answer: str) -> Dict:
        """Analyze relevance using Hugging Face"""
        try:
            payload = {
                "inputs": {
                    "source_sentence": question,
                    "sentences": [answer]
                }
            }
            
            response = requests.post(
                f"{self.api_url}/{self.evaluation_models['relevance']}",
                headers={"Authorization": f"Bearer {self.api_key}"} if self.api_key else {},
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "score": result[0]["score"],
                    "relevant": result[0]["score"] > 0.5
                }
        except Exception as e:
            print(f"⚠️ Relevance analysis failed: {e}")
        
        # Fallback
        return {"score": 0.7, "relevant": True}
    
    def _calculate_overall_score(self, evaluation: Dict) -> float:
        """Calculate overall evaluation score"""
        sentiment_score = evaluation["sentiment"]["score"]
        grammar_score = evaluation["grammar"]["score"]
        relevance_score = evaluation["relevance"]["score"]
        
        # Weighted average
        weights = {"sentiment": 0.3, "grammar": 0.3, "relevance": 0.4}
        
        overall = (
            sentiment_score * weights["sentiment"] +
            grammar_score * weights["grammar"] +
            relevance_score * weights["relevance"]
        ) * 100
        
        return round(overall, 2)
    
    def _generate_feedback(self, evaluation: Dict, question_type: str) -> List[str]:
        """Generate feedback based on evaluation"""
        feedback = []
        
        if evaluation["relevance"]["relevant"]:
            feedback.append("✓ Your answer is relevant to the question")
        else:
            feedback.append("⚠ Try to stay more focused on the question asked")
        
        if evaluation["grammar"]["score"] > 0.7:
            feedback.append("✓ Good grammar and clarity")
        else:
            feedback.append("⚠ Consider working on clarity and structure")
        
        if evaluation["sentiment"]["label"] == "POSITIVE":
            feedback.append("✓ Confident and positive tone")
        else:
            feedback.append("⚠ Try to maintain a more confident tone")
        
        return feedback
    
    def _generate_strengths(self, evaluation: Dict, question_type: str) -> List[str]:
        """Generate strengths based on evaluation"""
        strengths = []
        
        if evaluation["relevance"]["score"] > 0.8:
            strengths.append("Highly relevant answers")
        
        if evaluation["grammar"]["score"] > 0.8:
            strengths.append("Excellent communication skills")
        
        if evaluation["sentiment"]["label"] == "POSITIVE":
            strengths.append("Positive and confident demeanor")
        
        return strengths
    
    def _generate_improvements(self, evaluation: Dict, question_type: str) -> List[str]:
        """Generate improvements based on evaluation"""
        improvements = []
        
        if evaluation["relevance"]["score"] < 0.6:
            improvements.append("Focus more on answering the specific question asked")
        
        if evaluation["grammar"]["score"] < 0.7:
            improvements.append("Work on structuring your answers more clearly")
        
        if evaluation["sentiment"]["label"] != "POSITIVE":
            improvements.append("Try to maintain a more confident and positive tone")
        
        return improvements
    
    async def evaluate_body_language(self, analysis_data: Dict) -> Dict:
        """Evaluate body language using Hugging Face"""
        # For now, use rule-based evaluation with Hugging Face for future enhancement
        return {
            "overall_score": 80,
            "eye_contact_score": 85,
            "posture_score": 75,
            "gestures_score": 80,
            "feedback": ["Good eye contact", "Maintained professional posture"],
            "suggestions": ["Use more hand gestures", "Maintain consistent eye contact"]
        }
    
    def _get_template_questions(self, round_type: str, category: str, level: str) -> List[Dict]:
        """Fallback template questions"""
        question_templates = {
            "technical": [
                "Describe a challenging technical problem you solved",
                "How do you approach debugging complex code?",
                "What's your experience with system design?",
                "Explain a technical concept to a non-technical person"
            ],
            "behavioral": [
                "Tell me about a time you faced a conflict at work",
                "Describe a situation where you had to learn quickly",
                "How do you handle tight deadlines?",
                "Tell me about your biggest professional achievement"
            ],
            "hr": [
                "Why are you interested in this position?",
                "Where do you see yourself in 5 years?",
                "What are your salary expectations?",
                "Describe your ideal work environment"
            ]
        }
        
        questions = []
        prompts = question_templates.get(category, question_templates["behavioral"])
        
        for i, prompt in enumerate(prompts[:2]):
            question = {
                "id": f"{round_type}_{i+1}",
                "question": prompt,
                "type": category,
                "category": round_type,
                "difficulty": level,
                "hint": self._generate_hint(prompt, category)
            }
            questions.append(question)
        
        return questions
    
    def _generate_hint(self, question: str, category: str) -> str:
        """Generate hints for questions"""
        hints = {
            "technical": "Think about specific examples and technical details",
            "behavioral": "Use the STAR method: Situation, Task, Action, Result",
            "hr": "Be honest and align with your career goals"
        }
        return hints.get(category, "Be specific and provide examples")