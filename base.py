import cv2
import mediapipe as mp
import numpy as np

class HandTracker:
    """Base class for hand tracking functionality"""
    
    def __init__(self):
        # Initialize MediaPipe Hands
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
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
            results = self.hands.process(rgb)
            return frame, results
        return None, None
    
    def get_landmarks(self, results, frame_shape):
        """Extract hand landmarks as pixel coordinates"""
        if not results.multi_hand_landmarks:
            return None
        
        h, w, _ = frame_shape
        landmarks = []
        
        for hand_landmarks in results.multi_hand_landmarks:
            lm = [(int(l.x * w), int(l.y * h)) for l in hand_landmarks.landmark]
            landmarks.append({
                'landmarks': lm,
                'hand_landmarks': hand_landmarks,
                'palm': lm[9],  # Middle finger MCP (palm center)
                'wrist': lm[0],
                'thumb_tip': lm[4],
                'index_tip': lm[8],
                'middle_tip': lm[12],
                'ring_tip': lm[16],
                'pinky_tip': lm[20],
                'fingers': {
                    'thumb': [lm[2], lm[3], lm[4]],
                    'index': [lm[5], lm[6], lm[7], lm[8]],
                    'middle': [lm[9], lm[10], lm[11], lm[12]],
                    'ring': [lm[13], lm[14], lm[15], lm[16]],
                    'pinky': [lm[17], lm[18], lm[19], lm[20]]
                }
            })
        
        return landmarks
    
    def draw_hand_skeleton(self, frame, hand_landmarks):
        """Draw the hand skeleton on the frame"""
        self.mp_drawing.draw_landmarks(
            frame, 
            hand_landmarks, 
            self.mp_hands.HAND_CONNECTIONS
        )
    
    def is_finger_up(self, landmarks, finger_name):
        """Check if a finger is extended (up)"""
        finger_points = landmarks['fingers'][finger_name]
        
        if finger_name == 'thumb':
            # Thumb: check if tip is to the right of the joint
            return finger_points[2][0] > finger_points[0][0]
        else:
            # Other fingers: check if tip is above the joint
            return finger_points[3][1] < finger_points[0][1]
    
    def get_finger_count(self, landmarks):
        """Count how many fingers are up"""
        count = 0
        for finger in ['thumb', 'index', 'middle', 'ring', 'pinky']:
            if self.is_finger_up(landmarks, finger):
                count += 1
        return count
    
    def get_distance(self, point1, point2):
        """Calculate distance between two points"""
        return np.linalg.norm(np.array(point1) - np.array(point2))
    
    def release(self):
        """Release the camera"""
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()

