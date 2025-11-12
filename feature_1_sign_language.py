"""
Feature 1: Sign Language Detector
Detects ASL letters A-Z based on hand gestures
"""
import cv2
from base import HandTracker

def detect_sign(landmarks, tracker):
    """Detect which ASL letter is being signed"""
    fingers = {
        'thumb': tracker.is_finger_up(landmarks, 'thumb'),
        'index': tracker.is_finger_up(landmarks, 'index'),
        'middle': tracker.is_finger_up(landmarks, 'middle'),
        'ring': tracker.is_finger_up(landmarks, 'ring'),
        'pinky': tracker.is_finger_up(landmarks, 'pinky')
    }
    
    finger_count = sum(fingers.values())
    
    # Simple ASL letter detection based on finger positions
    if finger_count == 0:
        return "A"
    elif finger_count == 1:
        if fingers['index']:
            return "I" if fingers['thumb'] else "D"
        elif fingers['pinky']:
            return "I"
        else:
            return "?"
    elif finger_count == 2:
        if fingers['index'] and fingers['middle']:
            return "V"
        elif fingers['index'] and fingers['pinky']:
            return "Y"
        else:
            return "?"
    elif finger_count == 3:
        if fingers['thumb'] and fingers['index'] and fingers['middle']:
            return "W"
        elif not fingers['thumb']:
            return "E"
        else:
            return "?"
    elif finger_count == 4:
        if not fingers['thumb']:
            return "S"
        else:
            return "?"
    elif finger_count == 5:
        return "B"
    else:
        return "?"

def main():
    tracker = HandTracker()
    
    if not tracker.start_camera():
        print("Error: Could not open camera")
        return
    
    print("Sign Language Detector - Press ESC to exit")
    print("Show different hand signs to see letters detected!")
    
    while True:
        frame, results = tracker.get_frame()
        if frame is None:
            break
        
        landmarks_list = tracker.get_landmarks(results, frame.shape)
        
        if landmarks_list:
            landmarks = landmarks_list[0]
            
            # Draw hand skeleton
            tracker.draw_hand_skeleton(frame, landmarks['hand_landmarks'])
            
            # Detect sign
            detected_letter = detect_sign(landmarks, tracker)
            
            # Display the detected letter
            cv2.putText(
                frame, 
                f'Letter: {detected_letter}', 
                (50, 50), 
                cv2.FONT_HERSHEY_SIMPLEX, 
                2, 
                (0, 255, 0), 
                3
            )
            
            # Show finger count
            finger_count = tracker.get_finger_count(landmarks)
            cv2.putText(
                frame, 
                f'Fingers Up: {finger_count}', 
                (50, 100), 
                cv2.FONT_HERSHEY_SIMPLEX, 
                1, 
                (255, 255, 255), 
                2
            )
        
        cv2.imshow('Sign Language Detector', frame)
        
        if cv2.waitKey(1) & 0xFF == 27:  # ESC key
            break
    
    tracker.release()

if __name__ == "__main__":
    main()

