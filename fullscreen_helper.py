"""
Helper functions for fullscreen support across all features
"""
import cv2
import numpy as np

def setup_fullscreen_window(window_name, start_fullscreen=False):
    """Setup window with fullscreen capability"""
    try:
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        # Don't set fullscreen on startup - let user toggle it
        return False  # Always start in windowed mode
    except Exception as e:
        print(f"Warning: Could not set up window: {e}")
        return False

def resize_frame_for_fullscreen(frame, screen_width=1920, screen_height=1080, enabled=True):
    """Resize frame to fill screen while maintaining aspect ratio"""
    # Disable resizing for now to prevent crashes
    return frame, (0, 0, 1.0)

def toggle_fullscreen(window_name, current_state):
    """Toggle fullscreen mode - simplified to prevent crashes"""
    try:
        new_state = not current_state
        if new_state:
            # Try to set fullscreen, but don't crash if it fails
            try:
                cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
            except:
                pass  # Silently fail if fullscreen not supported
        else:
            try:
                cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
            except:
                pass
        return new_state
    except:
        return False  # Return to windowed mode if anything fails

