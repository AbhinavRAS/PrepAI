# from pymongo import MongoClient
# from typing import Dict, List, Optional
# import os
# from datetime import datetime

# class MongoDB:
#     def __init__(self):
#         self.connection_string = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
#         self.client = MongoClient(self.connection_string)
#         self.db = self.client["interview_agent"]
        
#         # Collections
#         self.interviews = self.db["interviews"]
#         self.candidates = self.db["candidates"]
#         self.questions = self.db["questions"]
#         self.analytics = self.db["analytics"]
    
#     async def create_interview(self, interview_data: Dict) -> str:
#         """Create new interview session"""
#         interview_data["created_at"] = datetime.now()
#         interview_data["status"] = "active"
        
#         result = self.interviews.insert_one(interview_data)
#         return str(result.inserted_id)
    
#     async def update_interview(self, interview_id: str, update_data: Dict) -> bool:
#         """Update interview session"""
#         update_data["updated_at"] = datetime.now()
        
#         result = self.interviews.update_one(
#             {"_id": interview_id},
#             {"$set": update_data}
#         )
#         return result.modified_count > 0
    
#     async def get_interview(self, interview_id: str) -> Optional[Dict]:
#         """Get interview by ID"""
#         interview = self.interviews.find_one({"_id": interview_id})
#         return interview
    
#     async def save_answer(self, interview_id: str, answer_data: Dict) -> bool:
#         """Save answer to interview"""
#         answer_data["timestamp"] = datetime.now()
        
#         result = self.interviews.update_one(
#             {"_id": interview_id},
#             {"$push": {"answers": answer_data}}
#         )
#         return result.modified_count > 0
    
#     async def complete_interview(self, interview_id: str, evaluation: Dict) -> bool:
#         """Complete interview with evaluation"""
#         update_data = {
#             "status": "completed",
#             "evaluation": evaluation,
#             "completed_at": datetime.now()
#         }
        
#         result = self.interviews.update_one(
#             {"_id": interview_id},
#             {"$set": update_data}
#         )
#         return result.modified_count > 0
    
#     async def get_candidate_interviews(self, candidate_email: str) -> List[Dict]:
#         """Get all interviews for a candidate"""
#         interviews = self.interviews.find(
#             {"candidate_email": candidate_email}
#         ).sort("created_at", -1)
        
#         return list(interviews)
    
#     async def save_video_analysis(self, interview_id: str, analysis_data: Dict) -> bool:
#         """Save video analysis data"""
#         analysis_data["timestamp"] = datetime.now()
        
#         result = self.interviews.update_one(
#             {"_id": interview_id},
#             {"$push": {"video_analysis": analysis_data}}
#         )
#         return result.modified_count > 0


from pymongo import MongoClient
from typing import Dict, List, Optional
import os
from datetime import datetime

class MongoDB:
    def __init__(self):
        self.connection_string = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
        self.client = MongoClient(self.connection_string)
        self.db = self.client["interview_agent"]
        
        # Collections
        self.interviews = self.db["interviews"]
        self.candidates = self.db["candidates"]
        self.questions = self.db["questions"]
        self.analytics = self.db["analytics"]
    
    async def create_interview(self, interview_data: Dict) -> str:
        """Create new interview session"""
        interview_data["created_at"] = datetime.now()
        interview_data["status"] = "active"
        
        result = self.interviews.insert_one(interview_data)
        return str(result.inserted_id)
    
    async def save_answer(self, interview_id: str, answer_data: Dict) -> bool:
        """Save answer to interview"""
        answer_data["timestamp"] = datetime.now()
        
        result = self.interviews.update_one(
            {"_id": interview_id},
            {"$push": {"answers": answer_data}}
        )
        return result.modified_count > 0
    
    async def get_interview(self, interview_id: str) -> Optional[Dict]:
        """Get interview by ID"""
        interview = self.interviews.find_one({"_id": interview_id})
        return interview

    async def complete_interview(self, interview_id: str, evaluation: Dict) -> bool:
        """Complete interview with evaluation"""
        update_data = {
            "status": "completed",
            "evaluation": evaluation,
            "completed_at": datetime.now()
        }
        
        result = self.interviews.update_one(
            {"_id": interview_id},
            {"$set": update_data}
        )
        return result.modified_count > 0

    async def get_candidate_interviews(self, candidate_email: str) -> List[Dict]:
        """Get all interviews for a candidate"""
        interviews = self.interviews.find(
            {"candidate_email": candidate_email}
        ).sort("created_at", -1)
        
        return list(interviews)
    
    async def save_video_analysis(self, interview_id: str, analysis_data: Dict) -> bool:
        """Save video analysis data"""
        analysis_data["timestamp"] = datetime.now()
        
        result = self.interviews.update_one(
            {"_id": interview_id},
            {"$push": {"video_analysis": analysis_data}}
        )
        return result.modified_count > 0