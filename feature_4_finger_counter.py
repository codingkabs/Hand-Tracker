"""
Feature 4: Finger Counter
Counts how many fingers are up and displays it
"""
import cv2
from base import HandTracker

def main():
    tracker = HandTracker()
    
    if not tracker.start_camera():
        print("Error: Could not open camera")
        return
    
    print("Finger Counter - Press ESC to exit")
    print("Show your hand and see how many fingers are detected!")
    
    while True:
        frame, results = tracker.get_frame()
        if frame is None:
            break
        
        landmarks_list = tracker.get_landmarks(results, frame.shape)
        
        if landmarks_list:
            landmarks = landmarks_list[0]
            
            # Draw hand skeleton
            tracker.draw_hand_skeleton(frame, landmarks['hand_landmarks'])
            
            # Count fingers
            finger_count = tracker.get_finger_count(landmarks)
            
            # Display count in large text
            text = str(finger_count)
            text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 5, 10)[0]
            text_x = (frame.shape[1] - text_size[0]) // 2
            text_y = (frame.shape[0] + text_size[1]) // 2
            
            # Draw background rectangle
            cv2.rectangle(frame, 
                         (text_x - 20, text_y - text_size[1] - 20),
                         (text_x + text_size[0] + 20, text_y + 20),
                         (0, 0, 0), -1)
            
            # Draw the number
            cv2.putText(frame, text, (text_x, text_y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 5, (0, 255, 0), 10)
            
            # Show which fingers are up
            finger_names = ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky']
            finger_status = []
            for i, finger in enumerate(['thumb', 'index', 'middle', 'ring', 'pinky']):
                is_up = tracker.is_finger_up(landmarks, finger)
                finger_status.append(f"{finger_names[i]}: {'UP' if is_up else 'DOWN'}")
            
            y_offset = 30
            for status in finger_status:
                cv2.putText(frame, status, (50, y_offset), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                y_offset += 25
        
        cv2.imshow('Finger Counter', frame)
        
        if cv2.waitKey(1) & 0xFF == 27:
            break
    
    tracker.release()

if __name__ == "__main__":
    main()

