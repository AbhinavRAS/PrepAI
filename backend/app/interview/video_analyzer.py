import cv2
import mediapipe as mp
import numpy as np
from typing import Dict, List, Optional
import os

class VideoAnalyzer:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.mp_face_mesh = mp.solutions.face_mesh
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            enable_segmentation=False,
            min_detection_confidence=0.5
        )
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
    
    async def analyze_video_frames(self, frame_paths: List[str]) -> Dict:
        """Analyze video frames for body language"""
        try:
            posture_scores = []
            eye_contact_scores = []
            hand_movement_scores = []
            
            for frame_path in frame_paths:
                if not os.path.exists(frame_path):
                    continue
                
                frame = cv2.imread(frame_path)
                if frame is None:
                    continue
                
                # Analyze posture
                posture_score = self._analyze_posture(frame)
                posture_scores.append(posture_score)
                
                # Analyze eye contact
                eye_contact_score = self._analyze_eye_contact(frame)
                eye_contact_scores.append(eye_contact_score)
                
                # Analyze hand movements
                hand_score = self._analyze_hand_movements(frame)
                hand_movement_scores.append(hand_score)
            
            # Calculate averages
            avg_posture = np.mean(posture_scores) if posture_scores else 70
            avg_eye_contact = np.mean(eye_contact_scores) if eye_contact_scores else 70
            avg_hand_movements = np.mean(hand_movement_scores) if hand_movement_scores else 70
            
            # Overall confidence score
            overall_confidence = (avg_posture + avg_eye_contact + avg_hand_movements) / 3
            
            # Generate feedback
            feedback = self._generate_body_language_feedback(avg_posture, avg_eye_contact, avg_hand_movements)
            
            return {
                'score': round(overall_confidence, 1),
                'posture': feedback['posture'],
                'eye_contact': feedback['eye_contact'],
                'hand_movements': feedback['hand_movements'],
                'confidence': feedback['confidence'],
                'detailed_scores': {
                    'posture': round(avg_posture, 1),
                    'eye_contact': round(avg_eye_contact, 1),
                    'hand_movements': round(avg_hand_movements, 1)
                }
            }
            
        except Exception as e:
            print(f"Error analyzing video: {e}")
            return {
                'score': 70,
                'posture': 'Unable to analyze posture',
                'eye_contact': 'Unable to analyze eye contact',
                'hand_movements': 'Unable to analyze hand movements',
                'confidence': 'Unable to assess confidence',
                'detailed_scores': {
                    'posture': 70,
                    'eye_contact': 70,
                    'hand_movements': 70
                }
            }
    
    def _analyze_posture(self, frame: np.ndarray) -> float:
        """Analyze body posture"""
        try:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.pose.process(rgb_frame)
            
            if results.pose_landmarks:
                landmarks = results.pose_landmarks.landmark
                
                # Check shoulder alignment
                left_shoulder = landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER]
                right_shoulder = landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER]
                
                # Check spine alignment (shoulders to hips)
                left_hip = landmarks[self.mp_pose.PoseLandmark.LEFT_HIP]
                right_hip = landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP]
                
                # Calculate posture score based on alignment
                shoulder_diff = abs(left_shoulder.y - right_shoulder.y)
                spine_alignment = abs((left_shoulder.y + right_shoulder.y) / 2 - (left_hip.y + right_hip.y) / 2)
                
                # Score: less difference = better posture
                posture_score = max(0, 100 - (shoulder_diff * 500 + spine_alignment * 300))
                return min(100, posture_score)
            
            return 70  # Default score if no pose detected
            
        except Exception as e:
            print(f"Error analyzing posture: {e}")
            return 70
    
    def _analyze_eye_contact(self, frame: np.ndarray) -> float:
        """Analyze eye contact (approximation using face orientation)"""
        try:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.face_mesh.process(rgb_frame)
            
            if results.multi_face_landmarks:
                face_landmarks = results.multi_face_landmarks[0]
                
                # Use key facial landmarks to estimate gaze direction
                left_eye = face_landmarks[33]  # Left eye center
                right_eye = face_landmarks[263]  # Right eye center
                nose_tip = face_landmarks[1]  # Nose tip
                
                # Simple heuristic: if eyes are roughly level and facing forward
                eye_level_diff = abs(left_eye.y - right_eye.y)
                eye_center_y = (left_eye.y + right_eye.y) / 2
                
                # Score based on eye alignment and position
                eye_score = max(0, 100 - (eye_level_diff * 1000))
                
                return min(100, eye_score)
            
            return 70  # Default score if no face detected
            
        except Exception as e:
            print(f"Error analyzing eye contact: {e}")
            return 70
    
    def _analyze_hand_movements(self, frame: np.ndarray) -> float:
        """Analyze hand movements and gestures"""
        try:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.pose.process(rgb_frame)
            
            if results.pose_landmarks:
                landmarks = results.pose_landmarks.landmark
                
                # Get hand positions
                left_wrist = landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST]
                right_wrist = landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST]
                
                # Check if hands are visible (not too close to body edges)
                frame_h, frame_w = frame.shape[:2]
                
                left_visible = (0.1 < left_wrist.x < 0.9 and 0.1 < left_wrist.y < 0.9)
                right_visible = (0.1 < right_wrist.x < 0.9 and 0.1 < right_wrist.y < 0.9)
                
                # Score based on appropriate hand usage
                if left_visible and right_visible:
                    # Both hands visible - good for gesturing
                    return 85
                elif left_visible or right_visible:
                    # One hand visible - moderate
                    return 75
                else:
                    # No hands visible - might be too stiff
                    return 60
            
            return 70  # Default score if no pose detected
            
        except Exception as e:
            print(f"Error analyzing hand movements: {e}")
            return 70
    
    def _generate_body_language_feedback(self, posture_score: float, eye_contact_score: float, hand_score: float) -> Dict:
        """Generate feedback based on scores"""
        feedback = {}
        
        # Posture feedback
        if posture_score >= 80:
            feedback['posture'] = "Excellent posture! You maintain an upright and confident position."
        elif posture_score >= 60:
            feedback['posture'] = "Good posture, but try to keep your back straighter."
        else:
            feedback['posture'] = "Work on maintaining better posture. Sit up straight and keep shoulders back."
        
        # Eye contact feedback
        if eye_contact_score >= 80:
            feedback['eye_contact'] = "Great eye contact! You appear engaged and confident."
        elif eye_contact_score >= 60:
            feedback['eye_contact'] = "Good eye contact, try to maintain it more consistently."
        else:
            feedback['eye_contact'] = "Try to maintain better eye contact. Look at the camera/interviewer regularly."
        
        # Hand movement feedback
        if hand_score >= 80:
            feedback['hand_movements'] = "Appropriate hand gestures that enhance your communication."
        elif hand_score >= 60:
            feedback['hand_movements'] = "Hand movements are okay, but could be more natural."
        else:
            feedback['hand_movements'] = "Try to use more natural hand gestures to emphasize points."
        
        # Overall confidence
        overall_score = (posture_score + eye_contact_score + hand_score) / 3
        if overall_score >= 80:
            feedback['confidence'] = "High confidence projected through body language."
        elif overall_score >= 60:
            feedback['confidence'] = "Moderate confidence. Small improvements would help."
        else:
            feedback['confidence'] = "Work on body language more."
        
async def analyze_video(frame_paths: List[str]) -> Dict:
    """Analyze video frames for body language"""
    video_analyzer = VideoAnalyzer()
    return await video_analyzer.analyze_video_frames(frame_paths)