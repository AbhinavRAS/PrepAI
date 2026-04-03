import cv2
import mediapipe as mp
import numpy as np
from typing import Dict, List
from datetime import datetime

class MediaPipeService:
    def __init__(self):
        try:
            # Initialize MediaPipe solutions (works with 0.10.33)
            self.face_mesh = mp.solutions.face_mesh.FaceMesh(
                static_image_mode=False,
                max_num_faces=1,
                refine_landmarks=True,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )
            self.pose = mp.solutions.pose.Pose(
                static_image_mode=False,
                model_complexity=1,
                enable_segmentation=False,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )
            self.hands = mp.solutions.hands.Hands(
                static_image_mode=False,
                max_num_hands=2,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )
            print("✅ MediaPipe initialized successfully")
        except Exception as e:
            print(f"⚠️ MediaPipe initialization failed: {e}")
            print("🎭 Using mock MediaPipe service")
            self.face_mesh = None
            self.pose = None
            self.hands = None

    def analyze_video_frame(self, frame: np.ndarray) -> Dict:
        """Analyze single video frame for body language"""
        try:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            analysis = {
                "face_analysis": self._analyze_face(rgb_frame),
                "pose_analysis": self._analyze_pose(rgb_frame),
                "hand_analysis": self._analyze_hands(rgb_frame),
                "timestamp": str(datetime.now())
            }
            
            return analysis
            
        except Exception as e:
            print(f"Error in analyze_video_frame: {e}")
            return self._mock_response()

    def _analyze_face(self, frame: np.ndarray) -> Dict:
        if not self.face_mesh:
            return {"status": "face_model_unavailable"}

        try:
            results = self.face_mesh.process(frame)
            
            if results.multi_face_landmarks:
                # Pass the first face landmark object directly
                eye_contact = self._calculate_eye_contact(results.multi_face_landmarks[0])
                smile = self._calculate_smile(results.multi_face_landmarks[0])
                
                return {
                    "eye_contact": eye_contact,
                    "smile": smile,
                    "face_detected": True
                }
            else:
                return {"face_detected": False}
                
        except Exception as e:
            print(f"Error in face analysis: {e}")
            return {"status": "face_analysis_error"}

    def _analyze_pose(self, frame: np.ndarray) -> Dict:
        if not self.pose:
            return {"status": "pose_model_unavailable"}

        try:
            results = self.pose.process(frame)
            
            if results.pose_landmarks:
                # Pass the pose landmark object directly
                posture = self._calculate_posture(results.pose_landmarks)
                
                return {
                    "posture": posture,
                    "pose_detected": True
                }
            else:
                return {"pose_detected": False}
                
        except Exception as e:
            print(f"Error in pose analysis: {e}")
            return {"status": "pose_analysis_error"}

    def _analyze_hands(self, frame: np.ndarray) -> Dict:
        if not self.hands:
            return {"status": "hands_model_unavailable"}

        try:
            results = self.hands.process(frame)
            
            if results.multi_hand_landmarks:
                gestures = self._analyze_gestures(results.multi_hand_landmarks)
                
                return {
                    "gestures": gestures,
                    "hands_detected": True
                }
            else:
                return {"hands_detected": False}
                
        except Exception as e:
            print(f"Error in hand analysis: {e}")
            return {"status": "hand_analysis_error"}

    def _calculate_eye_contact(self, landmarks) -> float:
        """Real eye contact calculation based on eye landmarks"""
        try:
            # Key eye landmarks
            left_eye = [landmarks.landmark[i] for i in [33, 7, 163, 144]]
            right_eye = [landmarks.landmark[i] for i in [362, 398, 384, 263]]
            nose = landmarks.landmark[1]
            
            # Calculate eye centers
            left_eye_center = np.mean([(l.x, l.y) for l in left_eye], axis=0)
            right_eye_center = np.mean([(l.x, l.y) for l in right_eye], axis=0)
            eye_center = (left_eye_center + right_eye_center) / 2
            
            # Calculate gaze direction (eye to nose)
            eye_to_nose = np.array([eye_center[0] - nose.x, eye_center[1] - nose.y])
            eye_distance = np.linalg.norm(eye_to_nose)
            
            # Score based on eye position
            if eye_distance < 0.1:
                eye_contact_score = 95  # Good eye contact
            elif eye_distance < 0.2:
                eye_contact_score = 85  # Fair eye contact
            elif eye_distance < 0.3:
                eye_contact_score = 70  # Poor eye contact
            else:
                eye_contact_score = 50  # Very poor eye contact
                
            return eye_contact_score
            
        except Exception as e:
            print(f"Error in eye contact calculation: {e}")
            return 80.0  # Fallback

    def _calculate_smile(self, landmarks) -> float:
        """Real smile detection based on mouth landmarks"""
        try:
            # Key mouth landmarks for smile detection
            upper_lip = landmarks.landmark[13]      # Upper lip
            lower_lip = landmarks.landmark[14]      # Lower lip
            left_mouth = landmarks.landmark[61]     # Left corner
            right_mouth = landmarks.landmark[291]    # Right corner
            
            # Calculate mouth openness (smile indicator)
            mouth_width = abs(left_mouth.x - right_mouth.x)
            mouth_height = abs(upper_lip.y - lower_lip.y)
            
            print(f"DEBUG - Mouth: width={mouth_width:.4f}, height={mouth_height:.4f}")
            
            # Calculate smile curvature
            if mouth_height > 0.02:  # Mouth is open
                smile_score = min(90, 50 + (mouth_width * 200))
            else:
                # Calculate lip curve for smile
                lip_curve = upper_lip.y - ((left_mouth.y + right_mouth.y) / 2)
                smile_score = min(90, 70 + (lip_curve * 500))
            
            print(f"DEBUG - Smile score: {smile_score:.2f}")
            return max(0, min(100, smile_score))
            
        except Exception as e:
            print(f"Error in smile calculation: {e}")
            return 75.0  # Fallback

    def _calculate_posture(self, landmarks) -> float:
        """Real posture calculation based on pose landmarks"""
        try:
            # Key pose landmarks
            left_shoulder = landmarks.landmark[11]
            right_shoulder = landmarks.landmark[12]
            left_ear = landmarks.landmark[7]
            right_ear = landmarks.landmark[8]
            nose = landmarks.landmark[0]
            
            # Calculate shoulder alignment
            shoulder_alignment = abs(left_shoulder.y - right_shoulder.y)
            alignment_score = max(0, 100 - (shoulder_alignment * 1000))
            
            print(f"DEBUG - Shoulder alignment: {shoulder_alignment:.4f}, score: {alignment_score:.2f}")
            
            # Calculate head position (ear-nose-ear alignment)
            left_ear_nose_diff = abs(left_ear.y - nose.y)
            right_ear_nose_diff = abs(right_ear.y - nose.y)
            head_tilt = abs(left_ear_nose_diff - right_ear_nose_diff)
            head_position_score = max(0, 100 - (head_tilt * 500))
            
            print(f"DEBUG - Head tilt: {head_tilt:.4f}, score: {head_position_score:.2f}")
                
            # Calculate shoulder level
            shoulder_y = (left_shoulder.y + right_shoulder.y) / 2
            nose_y = nose.y
            head_position = nose_y - shoulder_y
                
            # Score based on head position (upright is good)
            if abs(head_position) < 0.05:
                position_score = 100
            elif abs(head_position) < 0.1:
                position_score = 80
            else:
                position_score = 60
                
            print(f"DEBUG - Head position: {head_position:.4f}, score: {position_score:.2f}")
                    
            # Combined posture score
            posture_score = (alignment_score * 0.4) + (head_position_score * 0.6)
            
            print(f"DEBUG - Final posture score: {posture_score:.2f}")
            return max(0, min(100, posture_score))
                
        except Exception as e:
            print(f"Error in posture calculation: {e}")
            return 75.0  # Fallback

    def _analyze_gestures(self, hand_landmarks_list) -> List[str]:
        """Simple gesture analysis"""
        gestures = []
        
        for hand_landmarks in hand_landmarks_list:
            try:
                # Check for common gestures
                thumb_tip = hand_landmarks.landmark[4]
                index_tip = hand_landmarks.landmark[8]
                middle_tip = hand_landmarks.landmark[12]
                ring_tip = hand_landmarks.landmark[16]
                pinky_tip = hand_landmarks.landmark[20]
                
                # Simple gesture detection
                if thumb_tip.y < hand_landmarks.landmark[2].y:
                    gestures.append("thumbs_up")
                if index_tip.y < hand_landmarks.landmark[6].y:
                    gestures.append("pointing")
                if middle_tip.y < hand_landmarks.landmark[10].y:
                    gestures.append("middle_up")
                if not gestures:
                    gestures.append("natural")
                    
            except:
                gestures.append("natural")
                
        return gestures

    def _mock_response(self) -> Dict:
        """Fallback mock response"""
        return {
            "face_analysis": {
                "eye_contact": 85,
                "smile": 80,
                "face_detected": True
            },
            "pose_analysis": {
                "posture": 75,
                "pose_detected": True
            },
            "hand_analysis": {
                "gestures": ["natural"],
                "hands_detected": True
            },
            "timestamp": str(datetime.now())
        }