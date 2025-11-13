"""
Feature 4: Finger Counter
Counts how many fingers are up and displays it
"""
import cv2
from base import HandTracker
from fullscreen_helper import setup_fullscreen_window, resize_frame_for_fullscreen, toggle_fullscreen

def main():
    tracker = HandTracker()
    
    if not tracker.start_camera():
        print("Error: Could not open camera")
        return
    
    print("Finger Counter - Press ESC to exit")
    print("Press 'F' to toggle fullscreen")
    print("Show your hand and see how many fingers are detected!")
    
    fullscreen = setup_fullscreen_window('Finger Counter', start_fullscreen=True)
    
    while True:
        frame, results = tracker.get_frame()
        if frame is None:
            break
        
        # Resize for fullscreen
        frame, offset_info = resize_frame_for_fullscreen(frame)
        
        landmarks_list = tracker.get_landmarks(results, frame.shape)
        
        if landmarks_list:
            landmarks = landmarks_list[0]
            
            # Draw hand skeleton
            tracker.draw_hand_skeleton(frame, landmarks['hand_landmarks'])
            
            # Count fingers
            finger_count = tracker.get_finger_count(landmarks)
            
            # Display count in large text (slightly lower position)
            text = str(finger_count)
            text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 5, 10)[0]
            text_x = (frame.shape[1] - text_size[0]) // 2
            text_y = int(frame.shape[0] * 0.6)  # Slightly lower than center (60% down)
            
            # Draw background rectangle
            cv2.rectangle(frame, 
                         (text_x - 20, text_y - text_size[1] - 20),
                         (text_x + text_size[0] + 20, text_y + 20),
                         (0, 0, 0), -1)
            
            # Draw the number
            cv2.putText(frame, text, (text_x, text_y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 5, (0, 255, 0), 10)
            
            # Show which fingers are up (in black)
            finger_names = ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky']
            finger_status = []
            for i, finger in enumerate(['thumb', 'index', 'middle', 'ring', 'pinky']):
                is_up = tracker.is_finger_up(landmarks, finger)
                finger_status.append(f"{finger_names[i]}: {'UP' if is_up else 'DOWN'}")
            
            y_offset = 30
            for status in finger_status:
                cv2.putText(frame, status, (50, y_offset), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
                y_offset += 25
        
        cv2.imshow('Finger Counter', frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == 27:  # ESC
            break
        elif key == ord('f') or key == ord('F'):  # Toggle fullscreen
            fullscreen = toggle_fullscreen('Finger Counter', fullscreen)
    
    tracker.release()

if __name__ == "__main__":
    main()

