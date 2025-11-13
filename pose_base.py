import cv2
import mediapipe as mp
import numpy as np

class PoseTracker:
    """Base class for full body pose tracking functionality"""
    
    def __init__(self):
        # Initialize MediaPipe Pose
        self.mp_pose = mp.solutions.pose
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            smooth_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.cap = None
    
    def start_camera(self, camera_index=0):
        """Start the webcam"""
        self.cap = cv2.VideoCapture(camera_index)
        return self.cap.isOpened()
    
    def get_frame(self):
        """Get a frame from the camera"""
        if self.cap is None:
            return None, None
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.flip(frame, 1)  # Mirror the frame
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.pose.process(rgb)
            return frame, results
        return None, None
    
    def get_landmarks(self, results, frame_shape):
        """Extract pose landmarks as pixel coordinates"""
        if not results.pose_landmarks:
            return None
        
        h, w, _ = frame_shape
        landmarks = {}
        
        # Convert normalized landmarks to pixel coordinates
        for idx, landmark in enumerate(results.pose_landmarks.landmark):
            landmarks[idx] = (int(landmark.x * w), int(landmark.y * h))
        
        # Key body points (MediaPipe Pose landmark indices)
        return {
            'landmarks': landmarks,
            'pose_landmarks': results.pose_landmarks,
            # Face
            'nose': landmarks.get(0),
            # Shoulders
            'left_shoulder': landmarks.get(11),
            'right_shoulder': landmarks.get(12),
            # Elbows
            'left_elbow': landmarks.get(13),
            'right_elbow': landmarks.get(14),
            # Wrists
            'left_wrist': landmarks.get(15),
            'right_wrist': landmarks.get(16),
            # Hips
            'left_hip': landmarks.get(23),
            'right_hip': landmarks.get(24),
            # Knees
            'left_knee': landmarks.get(25),
            'right_knee': landmarks.get(26),
            # Ankles
            'left_ankle': landmarks.get(27),
            'right_ankle': landmarks.get(28),
        }
    
    def draw_pose(self, frame, pose_landmarks):
        """Draw the full body pose skeleton"""
        self.mp_drawing.draw_landmarks(
            frame,
            pose_landmarks,
            self.mp_pose.POSE_CONNECTIONS,
            landmark_drawing_spec=self.mp_drawing_styles.get_default_pose_landmarks_style()
        )
    
    def draw_body_outline(self, frame, landmarks_dict):
        """Draw a simple body outline"""
        if not landmarks_dict:
            return
        
        landmarks = landmarks_dict['landmarks']
        
        # Draw body outline using key points
        # Head circle
        if landmarks.get(0):  # Nose
            nose = landmarks[0]
            cv2.circle(frame, nose, 30, (0, 255, 0), 2)
        
        # Torso (shoulders to hips)
        if landmarks.get(11) and landmarks.get(12) and landmarks.get(23) and landmarks.get(24):
            left_shoulder = landmarks[11]
            right_shoulder = landmarks[12]
            left_hip = landmarks[23]
            right_hip = landmarks[24]
            
            # Draw torso rectangle
            top_left = (min(left_shoulder[0], right_shoulder[0]), min(left_shoulder[1], right_shoulder[1]))
            bottom_right = (max(left_hip[0], right_hip[0]), max(left_hip[1], right_hip[1]))
            cv2.rectangle(frame, top_left, bottom_right, (0, 255, 0), 2)
        
        # Arms
        if landmarks.get(11) and landmarks.get(13) and landmarks.get(15):
            cv2.line(frame, landmarks[11], landmarks[13], (0, 255, 0), 2)
            cv2.line(frame, landmarks[13], landmarks[15], (0, 255, 0), 2)
        if landmarks.get(12) and landmarks.get(14) and landmarks.get(16):
            cv2.line(frame, landmarks[12], landmarks[14], (0, 255, 0), 2)
            cv2.line(frame, landmarks[14], landmarks[16], (0, 255, 0), 2)
        
        # Legs
        if landmarks.get(23) and landmarks.get(25) and landmarks.get(27):
            cv2.line(frame, landmarks[23], landmarks[25], (0, 255, 0), 2)
            cv2.line(frame, landmarks[25], landmarks[27], (0, 255, 0), 2)
        if landmarks.get(24) and landmarks.get(26) and landmarks.get(28):
            cv2.line(frame, landmarks[24], landmarks[26], (0, 255, 0), 2)
            cv2.line(frame, landmarks[26], landmarks[28], (0, 255, 0), 2)
    
    def get_distance(self, point1, point2):
        """Calculate distance between two points"""
        if point1 is None or point2 is None:
            return 0
        return np.linalg.norm(np.array(point1) - np.array(point2))
    
    def release(self):
        """Release the camera"""
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()

