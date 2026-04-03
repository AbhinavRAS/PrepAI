import openai
import os
import json
import re
from typing import Dict, List, Any
from datetime import datetime
from openai import AsyncOpenAI

class HolisticEvaluationService:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.client = AsyncOpenAI(base_url="https://api.groq.com/openai/v1", api_key=self.api_key) if self.api_key else None
        
    def _parse_json_response(self, content: str) -> Any:
        content = content.strip()
        if content.startswith("```"):
            lines = content.split('\n')
            if lines[0].startswith("```"): lines.pop(0)
            if lines[-1].startswith("```"): lines.pop()
            content = '\n'.join(lines)
        match = re.search(r'\[.*\]|\{.*\}', content, re.DOTALL)
        if match:
            content = match.group(0)
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return eval(content)
    
    async def evaluate_session_holistically(self, interview_data: Dict, answers: List[Dict], body_language_data: List[Dict]) -> Dict:
        """Comprehensive session-level evaluation"""
        try:
            # Extract all answers for analysis
            all_answers = []
            question_answer_pairs = []
            
            for answer in answers:
                all_answers.append(answer["answer"])
                question_answer_pairs.append({
                    "question": answer["question"],
                    "answer": answer["answer"],
                    "question_type": answer.get("question_type", "unknown"),
                    "question_category": answer.get("question_category", "unknown")
                })
            
            # 1. Cross-Response Consistency Analysis
            consistency_analysis = await self._analyze_consistency(question_answer_pairs, interview_data["interview_type"])
            
            # 2. Technical Knowledge Depth Assessment
            technical_assessment = await self._assess_technical_depth(question_answer_pairs, interview_data["interview_type"])
            
            # 3. Communication Pattern Analysis
            communication_analysis = await self._analyze_communication_patterns(all_answers, answers)
            
            # 4. Aggregate Speech Analysis
            speech_analysis = self._aggregate_speech_analysis(answers)
            
            # 5. Aggregate Body Language Analysis
            category = self._detect_interview_category(interview_data["interview_type"])
            if category == 'government':
                body_language_analysis = self._aggregate_body_language_analysis(body_language_data)
            else:
                body_language_analysis = {"status": "Not Evaluated"}
            
            # 6. Generate Comprehensive Feedback
            comprehensive_feedback = await self._generate_comprehensive_feedback(
                consistency_analysis,
                technical_assessment,
                communication_analysis,
                speech_analysis,
                body_language_analysis,
                interview_data=interview_data
            )
            
            # 7. Calculate Weighted Overall Score
            overall_score = self._calculate_weighted_score(
                consistency_analysis,
                technical_assessment,
                communication_analysis,
                speech_analysis,
                body_language_analysis,
                interview_type=interview_data["interview_type"]
            )
            
            return {
                "session_id": interview_data["_id"],
                "candidate_name": interview_data["name"],
                "interview_type": interview_data["interview_type"],
                "overall_score": overall_score,
                "consistency_analysis": consistency_analysis,
                "technical_assessment": technical_assessment,
                "communication_analysis": communication_analysis,
                "speech_analysis": speech_analysis,
                "body_language_analysis": body_language_analysis,
                "comprehensive_feedback": comprehensive_feedback,
                "session_summary": self._generate_session_summary(comprehensive_feedback, overall_score),
                "evaluation_date": datetime.now(),
                "total_questions": len(interview_data["questions"]),
                "answered_questions": len(answers)
            }
            
        except Exception as e:
            print(f"⚠️ Holistic evaluation failed: {e}")
            return self._get_fallback_evaluation(interview_data, answers)
    
    async def _analyze_consistency(self, question_answer_pairs: List[Dict], interview_type: str) -> Dict:
        """Analyze consistency across all responses"""
        prompt = f"""
        Analyze the consistency of this candidate's responses across a {interview_type} interview:
        
        {self._format_qa_pairs(question_answer_pairs)}
        
        Evaluate:
        1. Logical consistency between answers
        2. Contradictions or conflicting statements
        3. Coherence of personal narrative/experience
        4. Alignment of skills and experience mentioned
        
        Return ONLY valid JSON with:
        - consistency_score (0-100)
        - contradictions_found (array)
        - strengths_consistency (array)
        - consistency_feedback (array)
        
        Do NOT wrap the output in markdown backticks.
        """
        
        try:
            response = await self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            
            return self._parse_json_response(response.choices[0].message.content)
        except Exception as e:
            print(f"⚠️ Consistency analysis failed: {e}")
            return {"consistency_score": 75, "contradictions_found": [], "strengths_consistency": [], "consistency_feedback": ["Good overall consistency"]}
    
    async def _assess_technical_depth(self, question_answer_pairs: List[Dict], interview_type: str) -> Dict:
        """Assess technical knowledge depth across all technical questions"""
        technical_qa = [qa for qa in question_answer_pairs if qa["question_type"] == "technical"]
        
        if not technical_qa:
            return {"technical_score": 0, "technical_feedback": ["No technical questions asked"]}
        
        prompt = f"""
        Assess the technical knowledge depth for this {interview_type} candidate:
        
        {self._format_qa_pairs(technical_qa)}
        
        Evaluate:
        1. Depth of technical understanding
        2. Problem-solving approach
        3. Practical vs theoretical knowledge
        4. Technical confidence and clarity
        5. Knowledge progression across questions
        
        Return ONLY valid JSON with:
        - technical_score (0-100)
        - technical_strengths (array)
        - technical_gaps (array)
        - technical_feedback (array)
        - knowledge_areas (array of topics mentioned)
        
        Do NOT wrap the output in markdown backticks.
        """
        
        try:
            response = await self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            
            return self._parse_json_response(response.choices[0].message.content)
        except Exception as e:
            print(f"⚠️ Technical assessment failed: {e}")
            return {"technical_score": 70, "technical_strengths": [], "technical_gaps": [], "technical_feedback": ["Technical assessment completed"]}
    
    async def _analyze_communication_patterns(self, all_answers: List[str], answers: List[Dict]) -> Dict:
        """Analyze communication patterns throughout the session"""
        prompt = f"""
        Analyze the communication patterns in these interview responses:
        
        {self._format_answers(all_answers)}
        
        Evaluate:
        1. Communication style consistency
        2. Clarity and articulation patterns
        3. Confidence level progression
        4. Response structure and organization
        5. Adaptability to different question types
        
        Return ONLY valid JSON with:
        - communication_score (0-100)
        - communication_strengths (array)
        - communication_improvements (array)
        - communication_patterns (array)
        - progression_analysis (string)
        
        Do NOT wrap the output in markdown backticks.
        """
        
        try:
            response = await self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            
            return self._parse_json_response(response.choices[0].message.content)
        except Exception as e:
            print(f"⚠️ Communication analysis failed: {e}")
            return {"communication_score": 75, "communication_strengths": [], "communication_improvements": [], "communication_patterns": [], "progression_analysis": "Steady communication throughout"}
    
    def _aggregate_speech_analysis(self, answers: List[Dict]) -> Dict:
        """Aggregate speech analysis across all responses"""
        total_speech_metrics = {
            "total_words": 0,
            "speech_rate_avg": 0,
            "hesitation_count_total": 0,
            "filler_words_total": 0,
            "confidence_avg": 0,
            "clarity_avg": 0
        }
        
        valid_speech_count = 0
        
        for answer in answers:
            speech_data = answer.get("speech_analysis", {})
            if speech_data:
                total_speech_metrics["total_words"] += speech_data.get("word_count", 0)
                total_speech_metrics["speech_rate_avg"] += speech_data.get("speech_rate", 150)
                total_speech_metrics["hesitation_count_total"] += speech_data.get("hesitation_count", 0)
                total_speech_metrics["filler_words_total"] += speech_data.get("filler_words", 0)
                total_speech_metrics["confidence_avg"] += speech_data.get("confidence_score", 0.8)
                total_speech_metrics["clarity_avg"] += speech_data.get("clarity_score", 0.8)
                valid_speech_count += 1
        
        if valid_speech_count > 0:
            total_speech_metrics["speech_rate_avg"] /= valid_speech_count
            total_speech_metrics["confidence_avg"] /= valid_speech_count
            total_speech_metrics["clarity_avg"] /= valid_speech_count
        
        total_speech_metrics["analysis_summary"] = {
            "overall_fluency": "Good" if total_speech_metrics["confidence_avg"] > 0.7 else "Needs Improvement",
            "speaking_pace": "Appropriate" if 120 <= total_speech_metrics["speech_rate_avg"] <= 160 else "Too Fast/Slow",
            "hesitation_level": "Low" if total_speech_metrics["hesitation_count_total"] < 5 else "High"
        }
        
        return total_speech_metrics
    
    def _aggregate_body_language_analysis(self, body_language_data: List[Dict]) -> Dict:
        """Aggregate body language analysis across the session"""
        if not body_language_data:
            return {"overall_score": 0, "feedback": ["No body language data available"]}
        
        aggregated_metrics = {
            "eye_contact_avg": 0,
            "posture_score_avg": 0,
            "gesture_frequency": {},
            "overall_engagement": 0,
            "professional_presence": 0
        }
        
        for analysis in body_language_data:
            face_analysis = analysis.get("face_analysis", {})
            pose_analysis = analysis.get("pose_analysis", {})
            
            if face_analysis.get("status") == "face_detected":
                aggregated_metrics["eye_contact_avg"] += face_analysis.get("eye_contact_percentage", 0)
            
            if pose_analysis.get("status") == "pose_detected":
                aggregated_metrics["posture_score_avg"] += pose_analysis.get("posture_score", 0)
        
        if body_language_data:
            aggregated_metrics["eye_contact_avg"] /= len(body_language_data)
            aggregated_metrics["posture_score_avg"] /= len(body_language_data)
            
            # Calculate overall scores
            aggregated_metrics["overall_engagement"] = (aggregated_metrics["eye_contact_avg"] + aggregated_metrics["posture_score_avg"]) / 2
            aggregated_metrics["professional_presence"] = aggregated_metrics["overall_engagement"]
        
        return aggregated_metrics
    
    async def _generate_comprehensive_feedback(self, *analyses, interview_data) -> Dict:
        """Generate comprehensive, personalized feedback"""
        prompt = f"""
        Generate comprehensive feedback for this {interview_data['interview_type']} interview candidate:
        
        Candidate: {interview_data['name']}
        Interview Type: {interview_data['interview_type']}
        Level: {interview_data['level']}
        
        Analysis Results:
        {self._format_analyses(analyses)}
        
        Generate personalized feedback including:
        1. Overall performance assessment
        2. Key strengths (3-5 points)
        3. Areas for improvement (3-5 points)
        4. Specific recommendations
        5. Career progression suggestions
        
        Return ONLY valid JSON with:
        - overall_assessment (string)
        - key_strengths (array)
        - improvement_areas (array)
        - specific_recommendations (array)
        - career_suggestions (array)
        - next_steps (array)
        
        Do NOT wrap the output in markdown backticks.
        """
        
        try:
            response = await self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            
            return self._parse_json_response(response.choices[0].message.content)
        except Exception as e:
            print(f"⚠️ Comprehensive feedback generation failed: {e}")
            return {
                "overall_assessment": "Good performance with room for growth",
                "key_strengths": ["Clear communication", "Technical knowledge"],
                "improvement_areas": ["Body language", "Response structure"],
                "specific_recommendations": ["Practice more structured answers"],
                "career_suggestions": ["Continue developing technical skills"],
                "next_steps": ["Focus on confidence building"]
            }
    
    def _detect_interview_category(self, interview_type: str) -> str:
        """Detect interview category for appropriate weightings"""
        interview_type_lower = interview_type.lower()
        
        # Technical interviews
        technical_keywords = ['software', 'developer', 'engineer', 'technical', 'programming', 'coding', 'devops', 'sre', 'data scientist', 'machine learning', 'ai', 'backend', 'frontend', 'full stack']
        
        # Behavioral interviews  
        behavioral_keywords = ['behavioral', 'manager', 'team lead', 'project manager', 'product manager', 'leadership', 'soft skills']
        
        # HR interviews
        hr_keywords = ['hr', 'human resources', 'recruiter', 'culture', 'fit', 'general', 'screening']
        
        # Government interviews
        government_keywords = ['ias', 'ips', 'government', 'civil service', 'public service', 'administrative']
        
        if any(keyword in interview_type_lower for keyword in government_keywords):
            return 'government'
        elif any(keyword in interview_type_lower for keyword in technical_keywords):
            return 'technical'
        elif any(keyword in interview_type_lower for keyword in behavioral_keywords):
            return 'behavioral'
        elif any(keyword in interview_type_lower for keyword in hr_keywords):
            return 'hr'
        else:
            return 'general'
    
    def _calculate_weighted_score(self, *analyses, interview_type) -> float:
        """Calculate weighted overall score based on interview type"""
        category = self._detect_interview_category(interview_type)
        
        weights = {
            'technical': {
                "technical": 0.4,
                "consistency": 0.2,
                "communication": 0.3,
                "speech": 0.1,
                "body_language": 0.0
            },
            'behavioral': {
                "technical": 0.1,
                "consistency": 0.3,
                "communication": 0.4,
                "speech": 0.2,
                "body_language": 0.0
            },
            'hr': {
                "technical": 0.1,
                "consistency": 0.3,
                "communication": 0.4,
                "speech": 0.2,
                "body_language": 0.0
            },
            'government': {
                "technical": 0.2,
                "consistency": 0.3,
                "communication": 0.2,
                "speech": 0.1,
                "body_language": 0.2
            },
            'general': {
                "technical": 0.2,
                "consistency": 0.3,
                "communication": 0.35,
                "speech": 0.15,
                "body_language": 0.0
            }
        }
        
        current_weights = weights.get(category, weights['general'])
        
        scores = {
            "technical": analyses[1].get("technical_score", 0),
            "consistency": analyses[0].get("consistency_score", 0),
            "communication": analyses[2].get("communication_score", 0),
            "speech": analyses[3].get("confidence_avg", 0) * 100,
            "body_language": analyses[4].get("overall_engagement", 0)
        }
        
        weighted_score = sum(scores[key] * current_weights[key] for key in current_weights)
        
        return round(weighted_score, 2)
    
    def _generate_session_summary(self, feedback: Dict, overall_score: float) -> str:
        """Generate a concise session summary"""
        assessment = feedback.get("overall_assessment", "Good performance")
        
        if overall_score >= 85:
            performance_level = "Excellent"
        elif overall_score >= 70:
            performance_level = "Good"
        elif overall_score >= 55:
            performance_level = "Satisfactory"
        else:
            performance_level = "Needs Improvement"
        
        return f"{performance_level} performance ({overall_score}/100). {assessment}"
    
    # Helper methods
    def _format_qa_pairs(self, pairs: List[Dict]) -> str:
        return "\n".join([f"Q: {qa['question']}\nA: {qa['answer']}" for qa in pairs])
    
    def _format_answers(self, answers: List[str]) -> str:
        return "\n".join([f"{i+1}. {answer}" for i, answer in enumerate(answers)])
    
    def _format_analyses(self, analyses) -> str:
        return "\n".join([str(analysis) for analysis in analyses])
    
    def _get_fallback_evaluation(self, interview_data: Dict, answers: List[Dict]) -> Dict:
        """Fallback evaluation if AI analysis fails"""
        return {
            "session_id": interview_data["_id"],
            "candidate_name": interview_data["name"],
            "interview_type": interview_data["interview_type"],
            "overall_score": 70.0,
            "consistency_analysis": {"consistency_score": 70},
            "technical_assessment": {"technical_score": 70},
            "communication_analysis": {"communication_score": 70},
            "speech_analysis": {"confidence_avg": 0.7},
            "body_language_analysis": {"overall_engagement": 70},
            "comprehensive_feedback": {
                "overall_assessment": "Completed interview successfully",
                "key_strengths": ["Participation", "Effort"],
                "improvement_areas": ["Preparation", "Confidence"]
            },
            "session_summary": "Interview completed with basic evaluation",
            "evaluation_date": datetime.now(),
            "total_questions": len(interview_data["questions"]),
            "answered_questions": len(answers)
        }