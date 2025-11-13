"""
Helper functions for fullscreen support across all features
"""
import cv2
import numpy as np

def setup_fullscreen_window(window_name, start_fullscreen=True):
    """Setup window with fullscreen capability"""
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    if start_fullscreen:
        cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    return start_fullscreen

def resize_frame_for_fullscreen(frame, screen_width=1920, screen_height=1080):
    """Resize frame to fill screen while maintaining aspect ratio"""
    original_height, original_width = frame.shape[:2]
    
    # Calculate scale to fit screen
    scale = min(screen_width / original_width, screen_height / original_height)
    new_width = int(original_width * scale)
    new_height = int(original_height * scale)
    
    # Resize frame
    resized_frame = cv2.resize(frame, (new_width, new_height))
    
    # If frame is smaller than screen, center it on black background
    if new_width < screen_width or new_height < screen_height:
        black_frame = np.zeros((screen_height, screen_width, 3), dtype=np.uint8)
        x_offset = (screen_width - new_width) // 2
        y_offset = (screen_height - new_height) // 2
        black_frame[y_offset:y_offset+new_height, x_offset:x_offset+new_width] = resized_frame
        return black_frame, (x_offset, y_offset, scale)
    
    return resized_frame, (0, 0, scale)

def toggle_fullscreen(window_name, current_state):
    """Toggle fullscreen mode"""
    new_state = not current_state
    if new_state:
        cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    else:
        cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
    return new_state

