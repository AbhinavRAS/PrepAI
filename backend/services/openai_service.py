import openai
import os
from typing import Dict, List, Any
from openai import AsyncOpenAI

class OpenAIService:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.client = AsyncOpenAI(base_url="https://api.groq.com/openai/v1", api_key=self.api_key) if self.api_key else None
    
    async def generate_questions(self, interview_type: str, rounds: List[str], level: str, name: str = None, email: str = None) -> List[Dict]:
        """Generate interview questions using OpenAI API"""
        questions = []
        
        for round_type in rounds:
            if round_type == "tr":
                category = "technical"
            elif round_type == "mr":
                category = "behavioral"
            else:
                category = "hr"
            
            prompt = f"""
            Generate 2 unique {category} interview questions for {name} ({email}) 
            applying for a {level} {interview_type} position.

            Consider their background and make questions personalized.
            Avoid generic templates. Make each question specific and engaging.
            Return as JSON array with "question" and "hint" fields.
            """
            
            try:
                response = await self.client.chat.completions.create(
                    model="llama3-70b-8192",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7
                )
                
                generated_questions = eval(response.choices[0].message.content)
                
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
                    
            except Exception as e:
                print(f"⚠️ OpenAI question generation failed: {e}")
                questions.extend(self._get_mock_questions(round_type, category, level))
        
        return questions
    
    async def generate_follow_up_question(self, question: str, answer: str, interview_type: str) -> str:
        prompt = f"""
        Based on this interview exchange:
        Question: {question}
        Answer: {answer}
        
        Generate one relevant follow-up question for a {interview_type} interview.
        The follow-up should dig deeper into their answer or explore related areas.
        Return only the question, no additional text.
        """
        
        try:
            response = await self.client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"⚠️ OpenAI follow-up generation failed: {e}")
            return "Can you tell me more about that?"

    # ... rest of the methods with proper indentation

    async def evaluate_answer(self, question: str, answer: str, question_type: str) -> Dict:
        """Evaluate answer using OpenAI API"""
        prompt = f"""
        Evaluate this interview answer:
        
        Question: {question}
        Answer: {answer}
        Question Type: {question_type}
        
        Provide evaluation as JSON with:
        - overall_score (0-100)
        - relevance_score (0-100)
        - clarity_score (0-100)
        - confidence_score (0-100)
        - feedback (array of strings)
        - strengths (array of strings)
        - improvements (array of strings)
        """
        
        try:
            response = await self.client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            
            evaluation = eval(response.choices[0].message.content)
            return evaluation
            
        except Exception as e:
            print(f"⚠️ OpenAI evaluation failed: {e}")
            # Fallback to mock evaluation
            return self._get_mock_evaluation(question, answer, question_type)
    
    async def evaluate_body_language(self, analysis_data: Dict) -> Dict:
        """Evaluate body language using OpenAI API"""
        prompt = f"""
        Evaluate this body language analysis for an interview:
        
        Analysis Data: {analysis_data}
        
        Provide evaluation as JSON with:
        - overall_score (0-100)
        - eye_contact_score (0-100)
        - posture_score (0-100)
        - gestures_score (0-100)
        - feedback (array of strings)
        - suggestions (array of strings)
        """
        
        try:
            response = await self.client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            
            evaluation = eval(response.choices[0].message.content)
            return evaluation
            
        except Exception as e:
            print(f"⚠️ OpenAI body language evaluation failed: {e}")
            # Fallback to mock evaluation
            return self._get_mock_body_language_evaluation(analysis_data)
    
    def _get_mock_questions(self, round_type: str, category: str, level: str) -> List[Dict]:
        """Fallback mock questions"""
        mock_questions = {
            "technical": [
                "Describe a challenging technical problem you solved",
                "How do you approach debugging complex code?"
            ],
            "behavioral": [
                "Tell me about a time you faced a conflict at work",
                "Describe a situation where you had to learn quickly"
            ],
            "hr": [
                "Why are you interested in this position?",
                "Where do you see yourself in 5 years?"
            ]
        }
        
        questions = []
        prompts = mock_questions.get(category, mock_questions["behavioral"])
        
        for i, prompt in enumerate(prompts):
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
    
    def _get_mock_evaluation(self, question: str, answer: str, question_type: str) -> Dict:
        """Fallback mock evaluation"""
        return {
            "overall_score": 75,
            "relevance_score": 80,
            "clarity_score": 70,
            "confidence_score": 75,
            "feedback": ["Good answer structure", "Could be more specific"],
            "strengths": ["Clear communication", "Relevant examples"],
            "improvements": ["Add more specific details", "Provide quantifiable results"]
        }
    
    def _get_mock_body_language_evaluation(self, analysis_data: Dict) -> Dict:
        """Fallback mock body language evaluation"""
        return {
            "overall_score": 80,
            "eye_contact_score": 85,
            "posture_score": 75,
            "gestures_score": 80,
            "feedback": ["Good eye contact", "Maintained professional posture"],
            "suggestions": ["Use more hand gestures", "Maintain consistent eye contact"]
        }
    
    def _generate_hint(self, question: str, category: str) -> str:
        """Generate hints for questions"""
        hints = {
            "technical": "Think about specific examples and technical details",
            "behavioral": "Use the STAR method: Situation, Task, Action, Result",
            "hr": "Be honest and align with your career goals"
        }
        return hints.get(category, "Be specific and provide examples")
        
    async def evaluate_answer_enhanced(self, question: str, answer: str, interview_type: str, question_type: str) -> Dict:
        """Enhanced real-time answer evaluation with multi-dimensional scoring"""
        try:
            prompt = f"""
            Evaluate this interview response on a scale of 1-10 for each dimension:

                Question: {question}
                Answer: {answer}
                Interview Type: {interview_type}
                Question Type: {question_type}

                Rate each dimension (1-10):
                1. Technical Accuracy
                2. Communication Clarity 
                3. Confidence Level
                4. Relevance to Question
                5. Completeness

                Also provide:
                - Specific feedback for each dimension
                - Overall score (1-100)
                - Key strengths
                - Improvement suggestions

                Return as JSON:
                {{
                    "technical_accuracy": 8,
                    "communication_clarity": 7,
                    "confidence_level": 8,
                    "relevance": 9,
                    "completeness": 7,
                    "overall_score": 78,
                    "feedback": {{
                        "technical": "Good technical understanding",
                        "communication": "Clear expression",
                        "confidence": "Shows confidence",
                        "relevance": "Directly addresses question",
                        "completeness": "Could add more details"
                    }},
                    "strengths": ["Technical knowledge", "Clear communication"],
                    "improvements": ["Add specific examples", "Provide more details"]
                }}
                """
                
            response = await self.client.chat.completions.create(
                    model="llama3-70b-8192",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3
                )
                
            return eval(response.choices[0].message.content)
                
        except Exception as e:
            print(f"⚠️ Enhanced evaluation failed: {e}")
            return self._get_enhanced_mock_evaluation()

    def _get_enhanced_mock_evaluation(self) -> Dict:
        """Fallback enhanced mock evaluation"""
        return {
                "technical_accuracy": 75,
                "communication_clarity": 80,
                "confidence_level": 70,
                "relevance": 85,
                "completeness": 72,
                "overall_score": 76,
                "feedback": {
                    "technical": "Good understanding of concepts",
                    "communication": "Clear and articulate",
                    "confidence": "Shows reasonable confidence",
                    "relevance": "Addresses the question well",
                    "completeness": "Could provide more details"
                },
                "strengths": ["Clear communication", "Relevant answers"],
                "improvements": ["Add specific examples", "Provide more depth"]
            }

    def calculate_confidence_score(self, answer_score: float, eye_contact: float, posture: float, smile: float) -> float:
        """Calculate combined confidence score from answer and video analysis"""
        return (
            answer_score * 0.6 +  # Answer quality (60%)
            eye_contact * 0.2 +    # Visual engagement (20%)
            posture * 0.1 +        # Professionalism (10%)
            smile * 0.1            # Positive demeanor (10%)
        )

    def get_performance_benchmark(self, interview_type: str, level: str) -> Dict:
        """Get performance benchmarks for comparison"""
        benchmarks = {
            'technical': {
                'senior': {'technical': 85, 'communication': 80, 'overall': 82},
                'junior': {'technical': 70, 'communication': 75, 'overall': 72},
                    'mid': {'technical': 75, 'communication': 77, 'overall': 76}
                },
                'behavioral': {
                    'senior': {'communication': 90, 'consistency': 85, 'overall': 87},
                    'junior': {'communication': 75, 'consistency': 70, 'overall': 72},
                    'mid': {'communication': 82, 'consistency': 77, 'overall': 79}
                },
                'hr': {
                    'senior': {'communication': 85, 'professionalism': 80, 'overall': 82},
                    'junior': {'communication': 70, 'professionalism': 75, 'overall': 72},
                    'mid': {'communication': 77, 'professionalism': 77, 'overall': 77}
                },
                'general': {
                    'senior': {'technical': 80, 'communication': 85, 'overall': 82},
                    'junior': {'technical': 70, 'communication': 75, 'overall': 72},
                    'mid': {'technical': 75, 'communication': 80, 'overall': 77}
                }
            }
            
        return benchmarks.get(interview_type, benchmarks['general']).get(level, benchmarks['general']['mid'])