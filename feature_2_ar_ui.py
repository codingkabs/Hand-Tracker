"""
Feature 2: AR UI Overlay (Original scary theme)
Futuristic AR UI with scary colors
"""
import cv2
import numpy as np
from base import HandTracker

# Colors for UI overlays (scary/horror theme)
CYAN = (0, 0, 139)  # Dark red/crimson
ORANGE = (0, 0, 255)  # Blood red
WHITE = (200, 200, 255)  # Slightly red-tinted white
RED = (0, 0, 200)  # Bright blood red
CORE = (139, 0, 139)  # Dark purple (glowing)

def draw_glow_circle(img, center, radius, color, thickness=2, glow=15):
    """Draw a circle with glow effect"""
    for g in range(glow, 0, -3):
        alpha = 0.08 + 0.12 * (g / glow)
        overlay = img.copy()
        cv2.circle(overlay, center, radius+g, color, thickness)
        cv2.addWeighted(overlay, alpha, img, 1-alpha, 0, img)
    cv2.circle(img, center, radius, color, thickness)

def draw_radial_ticks(img, center, radius, color, num_ticks=24, length=22, thickness=3):
    """Draw radial ticks around center"""
    for i in range(num_ticks):
        angle = np.deg2rad(i * (360/num_ticks))
        x1 = int(center[0] + (radius-length) * np.cos(angle))
        y1 = int(center[1] + (radius-length) * np.sin(angle))
        x2 = int(center[0] + radius * np.cos(angle))
        y2 = int(center[1] + radius * np.sin(angle))
        cv2.line(img, (x1, y1), (x2, y2), color, thickness)

def draw_core_pattern(img, center, radius):
    """Draw stylized core pattern"""
    for t in np.linspace(0, 2*np.pi, 40):
        r = radius * (0.7 + 0.3 * np.sin(6*t))
        x = int(center[0] + r * np.cos(t))
        y = int(center[1] + r * np.sin(t))
        cv2.circle(img, (x, y), 3, ORANGE, -1)
    cv2.circle(img, center, int(radius*0.6), CYAN, 2)
    cv2.circle(img, center, int(radius*0.4), ORANGE, 2)

def draw_hud_details(img, center):
    """Draw HUD details"""
    for i in range(8):
        angle = np.deg2rad(210 + i*10)
        x1 = int(center[0] + 140 * np.cos(angle))
        y1 = int(center[1] + 140 * np.sin(angle))
        x2 = int(center[0] + 170 * np.cos(angle))
        y2 = int(center[1] + 170 * np.sin(angle))
        cv2.line(img, (x1, y1), (x2, y2), CYAN, 4)
    for i in range(4):
        angle = np.deg2rad(270 + i*15)
        x = int(center[0] + 120 * np.cos(angle))
        y = int(center[1] + 120 * np.sin(angle))
        cv2.rectangle(img, (x-10, y-10), (x+10, y+10), CYAN, 2)

def draw_arc_segments(img, center):
    """Draw arc segments"""
    cv2.ellipse(img, center, (110,110), 0, -30, 210, CYAN, 3)
    cv2.ellipse(img, center, (100,100), 0, -30, 210, ORANGE, 2)
    cv2.ellipse(img, center, (80,80), 0, 0, 360, CYAN, 1)

def main():
    tracker = HandTracker()
    
    if not tracker.start_camera():
        print("Error: Could not open camera")
        return
    
    print("AR UI Overlay - Press ESC to exit")
    
    while True:
        frame, results = tracker.get_frame()
        if frame is None:
            break
        
        landmarks_list = tracker.get_landmarks(results, frame.shape)
        
        if landmarks_list:
            landmarks = landmarks_list[0]
            palm = landmarks['palm']
            lm = landmarks['landmarks']
            
            # Calculate gesture metrics
            tips = [landmarks['thumb_tip'], landmarks['index_tip'], 
                   landmarks['middle_tip'], landmarks['ring_tip'], landmarks['pinky_tip']]
            dists = [tracker.get_distance(tip, palm) for tip in tips]
            avg_dist = np.mean(dists)
            
            # Pinch detection
            pinch_dist = tracker.get_distance(landmarks['thumb_tip'], landmarks['index_tip'])
            pinch_val = int(100 - min(pinch_dist, 100))
            
            # Gesture logic
            if avg_dist > 70:
                # Open hand: full AR UI
                draw_glow_circle(frame, palm, 120, CYAN, 3, glow=30)
                draw_glow_circle(frame, palm, 90, CYAN, 2, glow=20)
                draw_glow_circle(frame, palm, 60, ORANGE, 2, glow=10)
                draw_radial_ticks(frame, palm, 120, CYAN, num_ticks=24, length=22, thickness=3)
                draw_core_pattern(frame, palm, 35)
                draw_hud_details(frame, palm)
                draw_arc_segments(frame, palm)
                
                # Dynamic lines to fingertips
                for i in [4, 8, 12, 16, 20]:
                    cv2.line(frame, palm, lm[i], CYAN, 2)
                    cv2.circle(frame, lm[i], 12, ORANGE, -1)
                
                # Angle calculation
                v1 = np.array(landmarks['thumb_tip']) - np.array(palm)
                v2 = np.array(landmarks['index_tip']) - np.array(palm)
                try:
                    angle = int(np.degrees(np.arccos(np.dot(v1, v2)/(np.linalg.norm(v1)*np.linalg.norm(v2)+1e-6))))
                except:
                    angle = 0
                cv2.putText(frame, f'{angle}°', (palm[0]+40, palm[1]-40), 
                           cv2.FONT_HERSHEY_DUPLEX, 1.5, (0, 0, 0), 4)
            elif pinch_val < 60:
                # Pinch gesture
                draw_glow_circle(frame, palm, 60, ORANGE, 3, glow=20)
                cv2.putText(frame, f'Pinch: {pinch_val}', (palm[0]-40, palm[1]-70), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, ORANGE, 3)
                for i in range(5):
                    cv2.ellipse(frame, (palm[0]+80, palm[1]), (30,30), 0, 180, 
                              180+pinch_val+i*10, ORANGE, 2)
            else:
                # Fist
                draw_glow_circle(frame, palm, 60, CYAN, 3, glow=20)
                cv2.putText(frame, 'FIST', (palm[0]-30, palm[1]-70), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, ORANGE, 3)
        
        cv2.imshow('Hand Tracking AR UI', frame)
        if cv2.waitKey(1) & 0xFF == 27:
            break
    
    tracker.release()

if __name__ == "__main__":
    main()

