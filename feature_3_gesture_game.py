"""
Feature 3: Rock Paper Scissors Game
Play rock-paper-scissors with hand gestures
"""
import cv2
import random
from base import HandTracker

def detect_gesture(landmarks, tracker):
    """Detect rock, paper, or scissors gesture"""
    finger_count = tracker.get_finger_count(landmarks)
    
    if finger_count == 0:
        return "ROCK"
    elif finger_count == 5:
        return "PAPER"
    elif finger_count == 2:
        # Check if it's V shape (scissors)
        if tracker.is_finger_up(landmarks, 'index') and tracker.is_finger_up(landmarks, 'middle'):
            return "SCISSORS"
    return "UNKNOWN"

def get_computer_choice():
    """Get random computer choice"""
    return random.choice(["ROCK", "PAPER", "SCISSORS"])

def determine_winner(player, computer):
    """Determine game winner"""
    if player == computer:
        return "TIE"
    elif (player == "ROCK" and computer == "SCISSORS") or \
         (player == "PAPER" and computer == "ROCK") or \
         (player == "SCISSORS" and computer == "PAPER"):
        return "YOU WIN!"
    else:
        return "COMPUTER WINS!"

def main():
    tracker = HandTracker()
    
    if not tracker.start_camera():
        print("Error: Could not open camera")
        return
    
    print("Rock Paper Scissors Game - Press ESC to exit")
    print("Show your gesture: Fist=Rock, Open Hand=Paper, V=Scissors")
    
    computer_choice = None
    player_choice = None
    result = None
    frame_count = 0
    
    while True:
        frame, results = tracker.get_frame()
        if frame is None:
            break
        
        frame_count += 1
        
        landmarks_list = tracker.get_landmarks(results, frame.shape)
        
        if landmarks_list:
            landmarks = landmarks_list[0]
            tracker.draw_hand_skeleton(frame, landmarks['hand_landmarks'])
            
            # Detect gesture every 30 frames (about 1 second at 30fps)
            if frame_count % 30 == 0:
                player_choice = detect_gesture(landmarks, tracker)
                if player_choice != "UNKNOWN":
                    computer_choice = get_computer_choice()
                    result = determine_winner(player_choice, computer_choice)
        
        # Display game info
        if player_choice:
            cv2.putText(frame, f'You: {player_choice}', (50, 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        if computer_choice:
            cv2.putText(frame, f'Computer: {computer_choice}', (50, 100), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        if result:
            cv2.putText(frame, result, (50, 150), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)
        
        # Instructions
        cv2.putText(frame, 'Fist=Rock | Open=Paper | V=Scissors', (50, frame.shape[0] - 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        cv2.imshow('Rock Paper Scissors', frame)
        
        if cv2.waitKey(1) & 0xFF == 27:
            break
    
    tracker.release()

if __name__ == "__main__":
    main()

