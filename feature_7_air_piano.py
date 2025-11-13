"""
Feature 7: Air Piano/Music Controller
Play virtual piano keys with finger taps
"""
import cv2
import numpy as np
from base import HandTracker
from fullscreen_helper import setup_fullscreen_window, resize_frame_for_fullscreen, toggle_fullscreen

class PianoKey:
    def __init__(self, x, y, width, height, note, color, is_black=False):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.note = note
        self.color = color
        self.is_black = is_black
        self.pressed = False
    
    def contains_point(self, point):
        """Check if point is inside key"""
        return (self.x <= point[0] <= self.x + self.width and
                self.y <= point[1] <= self.y + self.height)
    
    def draw(self, frame):
        """Draw the piano key"""
        color = (min(255, self.color[0] + 50), 
                min(255, self.color[1] + 50), 
                min(255, self.color[2] + 50)) if self.pressed else self.color
        
        cv2.rectangle(frame, (self.x, self.y), 
                     (self.x + self.width, self.y + self.height), 
                     color, -1)
        cv2.rectangle(frame, (self.x, self.y), 
                     (self.x + self.width, self.y + self.height), 
                     (255, 255, 255), 2)
        
        # Draw note label
        if not self.is_black:
            text_size = cv2.getTextSize(self.note, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0]
            text_x = self.x + (self.width - text_size[0]) // 2
            text_y = self.y + self.height - 10
            cv2.putText(frame, self.note, (text_x, text_y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)

class AirPiano:
    def __init__(self, frame_width, frame_height):
        self.keys = []
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.keyboard_y = frame_height - 200
        self.key_width = 60
        self.key_height = 150
        
        # Create white keys (C, D, E, F, G, A, B)
        white_notes = ['C', 'D', 'E', 'F', 'G', 'A', 'B']
        start_x = (frame_width - (len(white_notes) * self.key_width)) // 2
        
        for i, note in enumerate(white_notes):
            x = start_x + i * self.key_width
            self.keys.append(PianoKey(x, self.keyboard_y, self.key_width, 
                                    self.key_height, note, (255, 255, 255)))
        
        # Create black keys
        black_notes = ['C#', 'D#', None, 'F#', 'G#', 'A#']
        black_key_width = 40
        black_key_height = 100
        
        for i, note in enumerate(black_notes):
            if note:
                x = start_x + i * self.key_width + self.key_width - black_key_width // 2
                self.keys.append(PianoKey(x, self.keyboard_y, black_key_width, 
                                        black_key_height, note, (0, 0, 0), is_black=True))
    
    def check_key_press(self, finger_tip):
        """Check if any key is being pressed"""
        for key in self.keys:
            was_pressed = key.pressed
            key.pressed = key.contains_point(finger_tip)
            
            # If key just got pressed, play note
            if key.pressed and not was_pressed:
                return key.note
        return None
    
    def draw(self, frame):
        """Draw all piano keys"""
        # Draw white keys first
        for key in self.keys:
            if not key.is_black:
                key.draw(frame)
        
        # Draw black keys on top
        for key in self.keys:
            if key.is_black:
                key.draw(frame)

def main():
    tracker = HandTracker()
    
    if not tracker.start_camera():
        print("Error: Could not open camera")
        return
    
    print("Air Piano - Press ESC to exit")
    print("Press 'F' to toggle fullscreen")
    print("Point your index finger at keys to play notes!")
    
    fullscreen = setup_fullscreen_window('Air Piano', start_fullscreen=True)
    piano = None
    last_note = None
    note_display_time = 0
    
    while True:
        frame, results = tracker.get_frame()
        if frame is None:
            break
        
        # Resize for fullscreen
        frame, offset_info = resize_frame_for_fullscreen(frame)
        
        # Initialize piano with frame dimensions
        if piano is None:
            piano = AirPiano(frame.shape[1], frame.shape[0])
        
        landmarks_list = tracker.get_landmarks(results, frame.shape)
        
        if landmarks_list:
            landmarks = landmarks_list[0]
            
            # Draw hand skeleton
            tracker.draw_hand_skeleton(frame, landmarks['hand_landmarks'])
            
            # Get index finger tip
            index_tip = landmarks['index_tip']
            
            # Check for key press
            note = piano.check_key_press(index_tip)
            if note:
                last_note = note
                note_display_time = 30  # Display for 30 frames
                print(f"Playing: {note}")  # In real app, would play sound here
            
            # Draw indicator on finger tip
            cv2.circle(frame, index_tip, 15, (0, 255, 0), -1)
            cv2.circle(frame, index_tip, 15, (255, 255, 255), 2)
        
        # Draw piano
        piano.draw(frame)
        
        # Display current note
        if note_display_time > 0:
            cv2.putText(frame, f'Note: {last_note}', (50, 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)
            note_display_time -= 1
        
        # Instructions
        cv2.putText(frame, 'Point index finger at keys to play', 
                   (50, frame.shape[0] - 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        cv2.imshow('Air Piano', frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == 27:  # ESC
            break
        elif key == ord('f') or key == ord('F'):  # Toggle fullscreen
            fullscreen = toggle_fullscreen('Air Piano', fullscreen)
    
    tracker.release()

if __name__ == "__main__":
    main()

