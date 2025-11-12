"""
Main AR UI Launcher
Enhanced AR UI overlay with modular base system integration
Author: Kabir Suri (codingkabs)
"""
import cv2
import numpy as np
from base import HandTracker

# Enhanced color scheme (scary/horror theme with variations)
DARK_RED = (0, 0, 139)      # Dark red/crimson
BLOOD_RED = (0, 0, 255)     # Bright blood red
RED_TINT = (200, 200, 255)  # Red-tinted white
BRIGHT_RED = (0, 0, 200)    # Bright red
DARK_PURPLE = (139, 0, 139) # Dark purple glow
ACCENT = (0, 100, 255)      # Orange-red accent

def draw_enhanced_glow_circle(img, center, radius, color, thickness=2, glow=15, pulse=0):
    """Draw circle with enhanced glow and optional pulse effect"""
    # Pulse effect
    pulse_radius = int(radius * (1 + 0.1 * np.sin(pulse)))
    
    # Draw outer glow layers
    for g in range(glow, 0, -3):
        alpha = 0.08 + 0.12 * (g / glow)
        overlay = img.copy()
        cv2.circle(overlay, center, pulse_radius + g, color, thickness)
        cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0, img)
    
    # Draw main circle
    cv2.circle(img, center, pulse_radius, color, thickness)
    # Inner highlight
    cv2.circle(img, center, int(pulse_radius * 0.7), color, 1)

def draw_radial_ticks_enhanced(img, center, radius, color, num_ticks=24, length=22, thickness=3, rotation=0):
    """Draw radial ticks with rotation support"""
    for i in range(num_ticks):
        angle = np.deg2rad(i * (360/num_ticks) + rotation)
        x1 = int(center[0] + (radius - length) * np.cos(angle))
        y1 = int(center[1] + (radius - length) * np.sin(angle))
        x2 = int(center[0] + radius * np.cos(angle))
        y2 = int(center[1] + radius * np.sin(angle))
        cv2.line(img, (x1, y1), (x2, y2), color, thickness)
        # Add small dots at tick ends
        cv2.circle(img, (x2, y2), 2, color, -1)

def draw_core_pattern_enhanced(img, center, radius, pulse=0):
    """Enhanced core pattern with animation"""
    # Animated core pattern
    for t in np.linspace(0, 2*np.pi, 40):
        r = radius * (0.7 + 0.3 * np.sin(6*t + pulse))
        x = int(center[0] + r * np.cos(t))
        y = int(center[1] + r * np.sin(t))
        cv2.circle(img, (x, y), 3, BLOOD_RED, -1)
    
    # Concentric circles with glow
    cv2.circle(img, center, int(radius * 0.6), DARK_RED, 2)
    cv2.circle(img, center, int(radius * 0.4), BLOOD_RED, 2)
    cv2.circle(img, center, int(radius * 0.2), DARK_PURPLE, 2)

def draw_hud_details_enhanced(img, center):
    """Enhanced HUD with more details"""
    # Bottom HUD bars
    for i in range(8):
        angle = np.deg2rad(210 + i * 10)
        x1 = int(center[0] + 140 * np.cos(angle))
        y1 = int(center[1] + 140 * np.sin(angle))
        x2 = int(center[0] + 170 * np.cos(angle))
        y2 = int(center[1] + 170 * np.sin(angle))
        cv2.line(img, (x1, y1), (x2, y2), DARK_RED, 4)
    
    # HUD blocks with glow
    for i in range(4):
        angle = np.deg2rad(270 + i * 15)
        x = int(center[0] + 120 * np.cos(angle))
        y = int(center[1] + 120 * np.sin(angle))
        cv2.rectangle(img, (x - 10, y - 10), (x + 10, y + 10), DARK_RED, 2)
        cv2.circle(img, (x, y), 3, BLOOD_RED, -1)

def draw_arc_segments_enhanced(img, center):
    """Enhanced arc segments"""
    cv2.ellipse(img, center, (110, 110), 0, -30, 210, DARK_RED, 3)
    cv2.ellipse(img, center, (100, 100), 0, -30, 210, BLOOD_RED, 2)
    cv2.ellipse(img, center, (80, 80), 0, 0, 360, DARK_RED, 1)
    cv2.ellipse(img, center, (70, 70), 0, 0, 360, DARK_PURPLE, 1)

def draw_finger_connections_enhanced(frame, landmarks, palm):
    """Draw enhanced connections to fingertips"""
    finger_tips = [
        landmarks['thumb_tip'],
        landmarks['index_tip'],
        landmarks['middle_tip'],
        landmarks['ring_tip'],
        landmarks['pinky_tip']
    ]
    
    for tip in finger_tips:
        # Glowing line to palm
        cv2.line(frame, palm, tip, DARK_RED, 2)
        # Glowing tip
        cv2.circle(frame, tip, 12, BLOOD_RED, -1)
        cv2.circle(frame, tip, 15, DARK_PURPLE, 2)

def main():
    """Main AR UI application"""
    tracker = HandTracker()
    
    if not tracker.start_camera():
        print("Error: Could not open camera")
        print("Make sure your webcam is connected and not being used by another application.")
        return
    
    print("=" * 50)
    print("Hand Tracking AR UI - Enhanced Version")
    print("Author: Kabir Suri (codingkabs)")
    print("=" * 50)
    print("\nControls:")
    print("  - Open Hand: Full AR UI overlay")
    print("  - Pinch Gesture: Show pinch intensity")
    print("  - Fist: Simple indicator")
    print("  - ESC: Exit\n")
    
    frame_count = 0
    
    while True:
        frame, results = tracker.get_frame()
        if frame is None:
            break
        
        frame_count += 1
        pulse = frame_count * 0.1  # For animation
        rotation = frame_count * 0.5  # For rotating ticks
        
        landmarks_list = tracker.get_landmarks(results, frame.shape)
        
        if landmarks_list:
            landmarks = landmarks_list[0]
            palm = landmarks['palm']
            lm = landmarks['landmarks']
            
            # Draw hand skeleton
            tracker.draw_hand_skeleton(frame, landmarks['hand_landmarks'])
            
            # Calculate gesture metrics
            tips = [
                landmarks['thumb_tip'], landmarks['index_tip'],
                landmarks['middle_tip'], landmarks['ring_tip'],
                landmarks['pinky_tip']
            ]
            dists = [tracker.get_distance(tip, palm) for tip in tips]
            avg_dist = np.mean(dists)
            
            # Pinch detection
            pinch_dist = tracker.get_distance(landmarks['thumb_tip'], landmarks['index_tip'])
            pinch_val = int(100 - min(pinch_dist, 100))
            
            # Gesture-based UI rendering
            if avg_dist > 70:
                # Open hand: Full enhanced AR UI
                draw_enhanced_glow_circle(frame, palm, 120, DARK_RED, 3, glow=30, pulse=pulse)
                draw_enhanced_glow_circle(frame, palm, 90, DARK_RED, 2, glow=20, pulse=pulse)
                draw_enhanced_glow_circle(frame, palm, 60, BLOOD_RED, 2, glow=10, pulse=pulse)
                
                draw_radial_ticks_enhanced(frame, palm, 120, DARK_RED, num_ticks=24, 
                                          length=22, thickness=3, rotation=rotation)
                draw_core_pattern_enhanced(frame, palm, 35, pulse=pulse)
                draw_hud_details_enhanced(frame, palm)
                draw_arc_segments_enhanced(frame, palm)
                
                # Enhanced finger connections
                draw_finger_connections_enhanced(frame, landmarks, palm)
                
                # Calculate and display angle
                v1 = np.array(landmarks['thumb_tip']) - np.array(palm)
                v2 = np.array(landmarks['index_tip']) - np.array(palm)
                try:
                    angle = int(np.degrees(np.arccos(
                        np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-6)
                    )))
                except:
                    angle = 0
                
                # Enhanced text display
                cv2.putText(frame, f'{angle}°', (palm[0] + 40, palm[1] - 40),
                           cv2.FONT_HERSHEY_DUPLEX, 1.5, (0, 0, 0), 4)
                cv2.putText(frame, f'{angle}°', (palm[0] + 40, palm[1] - 40),
                           cv2.FONT_HERSHEY_DUPLEX, 1.5, BLOOD_RED, 2)
                
            elif pinch_val < 60:
                # Pinch gesture: Enhanced visualization
                draw_enhanced_glow_circle(frame, palm, 60, BLOOD_RED, 3, glow=20, pulse=pulse)
                
                # Enhanced text with background
                text = f'Pinch: {pinch_val}'
                text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 1, 3)[0]
                text_x = palm[0] - 40
                text_y = palm[1] - 70
                
                # Background rectangle
                cv2.rectangle(frame, (text_x - 5, text_y - text_size[1] - 5),
                             (text_x + text_size[0] + 5, text_y + 5), (0, 0, 0), -1)
                cv2.putText(frame, text, (text_x, text_y),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, BLOOD_RED, 3)
                
                # Animated arcs
                for i in range(5):
                    cv2.ellipse(frame, (palm[0] + 80, palm[1]), (30, 30), 0, 180,
                               180 + pinch_val + i * 10, BLOOD_RED, 2)
                    
            else:
                # Fist: Enhanced simple indicator
                draw_enhanced_glow_circle(frame, palm, 60, DARK_RED, 3, glow=20, pulse=pulse)
                
                # Enhanced text
                text = 'FIST'
                text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 1, 3)[0]
                text_x = palm[0] - 30
                text_y = palm[1] - 70
                
                cv2.rectangle(frame, (text_x - 5, text_y - text_size[1] - 5),
                             (text_x + text_size[0] + 5, text_y + 5), (0, 0, 0), -1)
                cv2.putText(frame, text, (text_x, text_y),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, BLOOD_RED, 3)
        
        # Display info overlay
        info_text = "Hand Tracking AR UI - Press ESC to exit"
        cv2.putText(frame, info_text, (10, frame.shape[0] - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        cv2.imshow('Hand Tracking AR UI - Enhanced', frame)
        
        if cv2.waitKey(1) & 0xFF == 27:  # ESC key
            break
    
    tracker.release()
    print("\nApplication closed. Thank you for using Hand Tracking AR UI!")

if __name__ == "__main__":
    main()
