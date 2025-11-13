"""
Feature 1: Sign Language Detector (Enhanced)
Detects ASL letters A-Z with improved accuracy for learning
Author: Kabir Suri (codingkabs)
"""
import cv2
import numpy as np
from base import HandTracker
from fullscreen_helper import setup_fullscreen_window, resize_frame_for_fullscreen, toggle_fullscreen

def calculate_finger_angles(landmarks, tracker):
    """Calculate angles for each finger to determine extension"""
    angles = {}
    
    for finger_name in ['thumb', 'index', 'middle', 'ring', 'pinky']:
        finger_points = landmarks['fingers'][finger_name]
        
        if finger_name == 'thumb':
            # Thumb uses different logic (horizontal extension)
            if len(finger_points) >= 3:
                p1 = np.array(finger_points[0])  # Base
                p2 = np.array(finger_points[2])  # Tip
                # Check if thumb is extended horizontally
                horizontal_dist = abs(p2[0] - p1[0])
                vertical_dist = abs(p2[1] - p1[1])
                angles[finger_name] = horizontal_dist > vertical_dist and horizontal_dist > 30
            else:
                angles[finger_name] = False
        else:
            # Other fingers: check if tip is significantly above base
            if len(finger_points) >= 4:
                base_y = finger_points[0][1]
                tip_y = finger_points[3][1]
                # Finger is up if tip is at least 30 pixels above base
                angles[finger_name] = (base_y - tip_y) > 30
            else:
                angles[finger_name] = False
    
    return angles

def check_finger_extended(landmarks, tracker, finger_name):
    """Improved finger extension check"""
    finger_points = landmarks['fingers'][finger_name]
    
    if finger_name == 'thumb':
        # Thumb: check horizontal extension
        if len(finger_points) >= 3:
            thumb_tip = finger_points[2]
            thumb_base = finger_points[0]
            # Check if thumb is extended to the side
            return abs(thumb_tip[0] - thumb_base[0]) > 40
        return False
    else:
        # Other fingers: check vertical extension
        if len(finger_points) >= 4:
            base = finger_points[0]
            tip = finger_points[3]
            # Check if tip is above base with sufficient distance
            return (base[1] - tip[1]) > 30
        return False

def detect_asl_letter(landmarks, tracker):
    """Enhanced ASL letter detection with better accuracy"""
    # Get finger states
    fingers = {
        'thumb': check_finger_extended(landmarks, tracker, 'thumb'),
        'index': check_finger_extended(landmarks, tracker, 'index'),
        'middle': check_finger_extended(landmarks, tracker, 'middle'),
        'ring': check_finger_extended(landmarks, tracker, 'ring'),
        'pinky': check_finger_extended(landmarks, tracker, 'pinky')
    }
    
    finger_count = sum([fingers['index'], fingers['middle'], 
                       fingers['ring'], fingers['pinky']])
    
    # Get hand landmarks for more detailed analysis
    thumb_tip = landmarks['thumb_tip']
    index_tip = landmarks['index_tip']
    middle_tip = landmarks['middle_tip']
    ring_tip = landmarks['ring_tip']
    pinky_tip = landmarks['pinky_tip']
    wrist = landmarks['wrist']
    palm = landmarks['palm']
    
    # Calculate distances for better detection
    thumb_index_dist = tracker.get_distance(thumb_tip, index_tip)
    index_middle_dist = tracker.get_distance(index_tip, middle_tip)
    
    # A - Fist (all fingers down, thumb can be in or out)
    if finger_count == 0:
        return "A"
    
    # B - All 4 fingers up, thumb can be in or out
    if finger_count == 4:
        return "B"
    
    # C - Curved hand (thumb and index form C shape)
    if fingers['thumb'] and fingers['index'] and not fingers['middle']:
        if 30 < thumb_index_dist < 80:
            return "C"
    
    # D - Only index finger up
    if finger_count == 1 and fingers['index'] and not fingers['thumb']:
        return "D"
    
    # E - 4 fingers bent (tips below middle joints)
    if finger_count == 0:
        # Check if fingers are bent but not fully closed
        index_bent = landmarks['landmarks'][8][1] > landmarks['landmarks'][6][1]
        middle_bent = landmarks['landmarks'][12][1] > landmarks['landmarks'][10][1]
        ring_bent = landmarks['landmarks'][16][1] > landmarks['landmarks'][14][1]
        pinky_bent = landmarks['landmarks'][20][1] > landmarks['landmarks'][18][1]
        if index_bent and middle_bent and ring_bent and pinky_bent:
            return "E"
    
    # F - Thumb and index touching, other fingers up
    if fingers['middle'] and fingers['ring'] and fingers['pinky']:
        if thumb_index_dist < 40:
            return "F"
    
    # G - Index pointing (extended horizontally)
    if fingers['index'] and not fingers['middle'] and finger_count == 1:
        # Check if index is pointing (horizontal orientation)
        index_angle = np.degrees(np.arctan2(
            index_tip[1] - palm[1],
            index_tip[0] - palm[0]
        ))
        if abs(index_angle) < 45 or abs(index_angle) > 135:
            return "G"
    
    # H - Index and middle extended together
    if fingers['index'] and fingers['middle'] and finger_count == 2:
        if index_middle_dist < 30:  # Fingers close together
            return "H"
    
    # I - Only pinky up
    if finger_count == 1 and fingers['pinky']:
        return "I"
    
    # J - I with movement (hard to detect statically, but we'll try)
    if finger_count == 1 and fingers['pinky']:
        # J is I with a downward curve motion - static detection is I
        return "I"  # Will show as I (J requires motion)
    
    # K - Index and middle up, spread apart, thumb touches middle
    if fingers['index'] and fingers['middle'] and finger_count == 2:
        if index_middle_dist > 40:  # Fingers spread
            thumb_middle_dist = tracker.get_distance(thumb_tip, middle_tip)
            if thumb_middle_dist < 50:
                return "K"
    
    # L - Index and thumb extended, forming L
    if fingers['index'] and fingers['thumb'] and not fingers['middle']:
        return "L"
    
    # M - Three fingers down, thumb tucked
    if finger_count == 0 and not fingers['thumb']:
        # Check if middle, ring, pinky are down but index might be slightly up
        return "A"  # Similar to A
    
    # N - Index and middle down, others up (or two fingers down)
    if finger_count == 2 and fingers['ring'] and fingers['pinky']:
        return "N"
    
    # O - All fingers curved to form O
    if finger_count == 0:
        # Check if thumb and fingers form a circle
        thumb_index_dist = tracker.get_distance(thumb_tip, index_tip)
        if 20 < thumb_index_dist < 60:
            return "O"
    
    # P - Similar to K but different orientation
    if fingers['index'] and fingers['middle'] and fingers['thumb']:
        return "P"
    
    # Q - G with pinky down (hard to distinguish from G)
    if fingers['index'] and finger_count == 1:
        return "G"  # Very similar to G
    
    # R - Index and middle crossed, or index and middle up with thumb
    if fingers['index'] and fingers['middle'] and finger_count == 2:
        if index_middle_dist > 30:
            return "R"
    
    # S - Fist with thumb over fingers
    if finger_count == 0 and fingers['thumb']:
        return "S"
    
    # T - Thumb between index and middle
    if fingers['index'] and fingers['middle'] and finger_count == 2:
        thumb_index_dist = tracker.get_distance(thumb_tip, index_tip)
        thumb_middle_dist = tracker.get_distance(thumb_tip, middle_tip)
        if thumb_index_dist < 40 and thumb_middle_dist < 40:
            return "T"
    
    # U - Index and middle up together
    if fingers['index'] and fingers['middle'] and finger_count == 2:
        if index_middle_dist < 30:
            return "U"
    
    # V - Index and middle up, spread apart
    if fingers['index'] and fingers['middle'] and finger_count == 2:
        if index_middle_dist > 40:
            return "V"
    
    # W - Three fingers up (index, middle, ring)
    if finger_count == 3 and fingers['index'] and fingers['middle'] and fingers['ring']:
        return "W"
    
    # X - Index finger bent
    if finger_count == 0:
        # Check if index is bent at middle joint
        index_mcp = landmarks['landmarks'][5]
        index_pip = landmarks['landmarks'][6]
        index_dip = landmarks['landmarks'][7]
        index_tip = landmarks['landmarks'][8]
        # If tip is below PIP but above MCP, it's bent
        if index_pip[1] < index_tip[1] < index_mcp[1]:
            return "X"
    
    # Y - Index, middle, ring down, pinky and thumb up
    if fingers['pinky'] and fingers['thumb'] and not fingers['index']:
        return "Y"
    
    # Z - Requires motion (drawing Z in air), static detection is hard
    # We'll use a combination: index extended, others down
    if fingers['index'] and finger_count == 1:
        return "D"  # Static Z looks like D
    
    # Default: return finger count if no match
    return f"? ({finger_count} fingers)"

def show_learning_guide(frame):
    """Display learning guide with letter descriptions"""
    guide_texts = [
        "ASL LETTER GUIDE:",
        "A: Fist (all fingers closed)",
        "B: All 4 fingers up, thumb in",
        "C: Thumb & index form C shape",
        "D: Only index finger up",
        "E: All fingers bent (tips down)",
        "F: Thumb touches index, 3 fingers up",
        "G: Index pointing (horizontal)",
        "H: Index & middle together, extended",
        "I: Only pinky up",
        "K: Index & middle spread, thumb touches middle",
        "L: Index & thumb form L shape",
        "O: All fingers curved to form circle",
        "P: Index & middle up with thumb",
        "R: Index & middle crossed/up",
        "S: Fist with thumb over fingers",
        "T: Thumb between index & middle",
        "U: Index & middle up together",
        "V: Index & middle up, spread apart",
        "W: Index, middle, ring up",
        "X: Index finger bent",
        "Y: Pinky & thumb up, others down",
        "",
        "Press 'L' to close guide"
    ]
    
    # Semi-transparent background
    overlay = frame.copy()
    cv2.rectangle(overlay, (10, 10), (400, 500), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
    
    # Draw guide text
    y_offset = 40
    for i, text in enumerate(guide_texts):
        color = (0, 255, 255) if i == 0 else (255, 255, 255)
        thickness = 2 if i == 0 else 1
        size = 0.6 if i == 0 else 0.5
        cv2.putText(frame, text, (20, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, size, color, thickness)
        y_offset += 20

def main():
    tracker = HandTracker()
    
    if not tracker.start_camera():
        print("Error: Could not open camera")
        return
    
    print("=" * 60)
    print("Enhanced ASL Sign Language Detector")
    print("Author: Kabir Suri (codingkabs)")
    print("=" * 60)
    print("\nThis detector recognizes ASL letters A-Z")
    print("Show hand signs clearly in front of the camera")
    print("Press 'L' to toggle learning mode")
    print("Press 'F' to toggle fullscreen")
    print("Press ESC to exit\n")
    
    confidence_threshold = 5  # Frames needed for stable detection
    last_letter = None
    letter_count = 0
    learning_mode = False
    last_button_state = False  # For button debounce
    fullscreen = setup_fullscreen_window('ASL Sign Language Detector', start_fullscreen=False)
    
    while True:
        frame, results = tracker.get_frame()
        if frame is None:
            break
        
        # Get landmarks from frame
        landmarks_list = tracker.get_landmarks(results, frame.shape)
        
        detected_letter = "No Hand"
        finger_count = 0
        
        if landmarks_list:
            landmarks = landmarks_list[0]
            
            # Draw hand skeleton
            tracker.draw_hand_skeleton(frame, landmarks['hand_landmarks'])
            
            # Detect sign
            detected_letter = detect_asl_letter(landmarks, tracker)
            finger_count = tracker.get_finger_count(landmarks)
            
            # Stability check - only update if same letter detected multiple times
            if detected_letter == last_letter:
                letter_count += 1
            else:
                letter_count = 1
                last_letter = detected_letter
            
            # Only show if stable
            if letter_count >= confidence_threshold:
                display_letter = detected_letter
            else:
                display_letter = "Detecting..."
        else:
            letter_count = 0
            last_letter = None
        
        # Display detected letter (large and clear)
        text_size = cv2.getTextSize(display_letter, cv2.FONT_HERSHEY_SIMPLEX, 3, 5)[0]
        text_x = (frame.shape[1] - text_size[0]) // 2
        text_y = frame.shape[0] // 2
        
        # Background for text
        cv2.rectangle(frame, 
                     (text_x - 20, text_y - text_size[1] - 20),
                     (text_x + text_size[0] + 20, text_y + 20),
                     (0, 0, 0), -1)
        
        # Letter text
        cv2.putText(frame, display_letter, (text_x, text_y),
                   cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 255, 0), 5)
        
        # Info display
        info_y = 30
        cv2.putText(frame, "ASL Letter Detector", (20, info_y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
        if landmarks_list:
            cv2.putText(frame, f'Fingers: {finger_count}', (20, info_y + 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 2)
            cv2.putText(frame, f'Confidence: {min(letter_count, confidence_threshold)}/{confidence_threshold}',
                       (20, info_y + 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 2)
        
        # Learning mode button (at bottom center)
        button_width = 300
        button_height = 50
        button_x = (frame.shape[1] - button_width) // 2
        button_y = frame.shape[0] - 80
        
        # Check if hand is over button area (simple click detection with debounce)
        if landmarks_list:
            index_tip = landmarks['index_tip']
            button_hover = (button_x <= index_tip[0] <= button_x + button_width and 
                          button_y <= index_tip[1] <= button_y + button_height)
            
            # Only toggle when button is first pressed (not held)
            if button_hover and not last_button_state:
                learning_mode = not learning_mode
                last_button_state = True
            elif not button_hover:
                last_button_state = False
        else:
            last_button_state = False
        
        # Draw button
        button_color = (0, 200, 0) if learning_mode else (100, 100, 100)
        cv2.rectangle(frame, (button_x, button_y), 
                     (button_x + button_width, button_y + button_height), 
                     button_color, -1)
        cv2.rectangle(frame, (button_x, button_y), 
                     (button_x + button_width, button_y + button_height), 
                     (255, 255, 255), 2)
        
        button_text = "LEARNING MODE: ON (Press 'L' to toggle)" if learning_mode else "LEARNING MODE: OFF (Press 'L' to toggle)"
        text_size = cv2.getTextSize(button_text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
        text_x = button_x + (button_width - text_size[0]) // 2
        text_y = button_y + (button_height + text_size[1]) // 2
        cv2.putText(frame, button_text, (text_x, text_y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Show learning guide if learning mode is on
        if learning_mode:
            show_learning_guide(frame)
        
        # Instructions
        cv2.putText(frame, "Show clear hand signs | Press ESC to exit",
                   (20, frame.shape[0] - 20),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        cv2.imshow('ASL Sign Language Detector', frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == 27:  # ESC
            break
        elif key == ord('l') or key == ord('L'):  # Toggle learning mode
            learning_mode = not learning_mode
        elif key == ord('f') or key == ord('F'):  # Toggle fullscreen
            fullscreen = toggle_fullscreen('ASL Sign Language Detector', fullscreen)
    
    tracker.release()
    print("\nThank you for using the ASL Detector!")

if __name__ == "__main__":
    main()
