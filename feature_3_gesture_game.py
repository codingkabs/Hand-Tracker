"""
Feature 3: Rock Paper Scissors Game (Enhanced)
Play rock-paper-scissors with countdown timer and scoring
Author: Kabir Suri (codingkabs)
"""
import cv2
import random
import time
from base import HandTracker
from fullscreen_helper import setup_fullscreen_window, resize_frame_for_fullscreen, toggle_fullscreen

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
        return "TIE", 0, 0  # 0 = tie, 1 = player wins, 2 = computer wins
    elif (player == "ROCK" and computer == "SCISSORS") or \
         (player == "PAPER" and computer == "ROCK") or \
         (player == "SCISSORS" and computer == "PAPER"):
        return "YOU WIN!", 1, 0
    else:
        return "COMPUTER WINS!", 0, 1

def draw_button(frame, x, y, width, height, text, color=(100, 100, 100)):
    """Draw a button on the frame"""
    cv2.rectangle(frame, (x, y), (x + width, y + height), color, -1)
    cv2.rectangle(frame, (x, y), (x + width, y + height), (255, 255, 255), 2)
    
    text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)[0]
    text_x = x + (width - text_size[0]) // 2
    text_y = y + (height + text_size[1]) // 2
    cv2.putText(frame, text, (text_x, text_y),
               cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    return (x, y, x + width, y + height)

def check_button_click(point, button_area):
    """Check if point is within button area"""
    x, y, x2, y2 = button_area
    return x <= point[0] <= x2 and y <= point[1] <= y2

def main():
    tracker = HandTracker()
    
    if not tracker.start_camera():
        print("Error: Could not open camera")
        return
    
    print("=" * 60)
    print("Rock Paper Scissors Game - Enhanced")
    print("Author: Kabir Suri (codingkabs)")
    print("=" * 60)
    print("\nFirst to 5 points wins!")
    print("Press 'S' or click START button to begin")
    print("Press 'F' to toggle fullscreen")
    print("Press ESC to exit\n")
    
    # Game state
    game_state = "MENU"  # MENU, COUNTDOWN, RESULT, VICTORY, REPLAY
    player_score = 0
    computer_score = 0
    countdown_number = 3
    countdown_start_time = 0
    player_choice = None
    computer_choice = None
    result_text = None
    last_frame_time = time.time()
    fullscreen = setup_fullscreen_window('Rock Paper Scissors', start_fullscreen=False)
    
    while True:
        frame, results = tracker.get_frame()
        if frame is None:
            break
        
        current_time = time.time()
        frame_time = current_time - last_frame_time
        last_frame_time = current_time
        
        landmarks_list = tracker.get_landmarks(results, frame.shape)
        
        # Draw hand skeleton if hand detected
        if landmarks_list:
            landmarks = landmarks_list[0]
            tracker.draw_hand_skeleton(frame, landmarks['hand_landmarks'])
            index_tip = landmarks['index_tip']
        else:
            index_tip = None
        
        # Game state machine
        if game_state == "MENU":
            # Draw start button
            button_area = draw_button(frame, 
                                     frame.shape[1] // 2 - 150, 
                                     frame.shape[0] // 2 - 25,
                                     300, 50, 
                                     "START GAME", 
                                     (0, 200, 0))
            
            # Check for button click or 'S' key
            if index_tip and check_button_click(index_tip, button_area):
                game_state = "COUNTDOWN"
                countdown_number = 3
                countdown_start_time = current_time
            elif cv2.waitKey(1) & 0xFF == ord('s'):
                game_state = "COUNTDOWN"
                countdown_number = 3
                countdown_start_time = current_time
            
            # Display scores
            cv2.putText(frame, f"Player: {player_score}  |  Computer: {computer_score}", 
                       (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            cv2.putText(frame, "First to 5 points wins!", 
                       (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (200, 200, 200), 2)
        
        elif game_state == "COUNTDOWN":
            elapsed = current_time - countdown_start_time
            
            # Update countdown every second
            if elapsed >= 1.0 and countdown_number > 0:
                countdown_number -= 1
                countdown_start_time = current_time
                elapsed = 0
            
            # Display countdown
            if countdown_number > 0:
                countdown_text = str(countdown_number)
                text_size = cv2.getTextSize(countdown_text, cv2.FONT_HERSHEY_SIMPLEX, 5, 10)[0]
                text_x = (frame.shape[1] - text_size[0]) // 2
                text_y = (frame.shape[0] + text_size[1]) // 2
                cv2.putText(frame, countdown_text, (text_x, text_y),
                           cv2.FONT_HERSHEY_SIMPLEX, 5, (0, 255, 255), 10)
            elif elapsed >= 0.5:  # After "SHOOT"
                # Detect gesture
                if landmarks_list:
                    player_choice = detect_gesture(landmarks, tracker)
                    if player_choice == "UNKNOWN":
                        player_choice = "ROCK"  # Default if unclear
                else:
                    player_choice = "ROCK"  # Default if no hand
                
                computer_choice = get_computer_choice()
                result_text, player_points, comp_points = determine_winner(player_choice, computer_choice)
                
                player_score += player_points
                computer_score += comp_points
                
                game_state = "RESULT"
                result_start_time = current_time
        
        elif game_state == "RESULT":
            # Show results for 3 seconds
            elapsed = current_time - result_start_time
            
            # Display choices
            cv2.putText(frame, f'You: {player_choice}', (50, 100), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
            cv2.putText(frame, f'Computer: {computer_choice}', (50, 150), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 0, 0), 3)
            
            # Display result
            result_size = cv2.getTextSize(result_text, cv2.FONT_HERSHEY_SIMPLEX, 2, 4)[0]
            result_x = (frame.shape[1] - result_size[0]) // 2
            cv2.putText(frame, result_text, (result_x, 250), 
                       cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 4)
            
            # Display scores
            cv2.putText(frame, f"Player: {player_score}  |  Computer: {computer_score}", 
                       (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2)
            
            if elapsed >= 3.0:
                # Check for victory
                if player_score >= 5 or computer_score >= 5:
                    game_state = "VICTORY"
                else:
                    # Return to menu for next round
                    game_state = "MENU"
        
        elif game_state == "VICTORY":
            # Show victory screen
            winner = "YOU WIN THE GAME!" if player_score >= 5 else "COMPUTER WINS THE GAME!"
            winner_size = cv2.getTextSize(winner, cv2.FONT_HERSHEY_SIMPLEX, 2, 4)[0]
            winner_x = (frame.shape[1] - winner_size[0]) // 2
            
            cv2.putText(frame, winner, (winner_x, frame.shape[0] // 2 - 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 4)
            cv2.putText(frame, f"Final Score: {player_score} - {computer_score}", 
                       (frame.shape[1] // 2 - 200, frame.shape[0] // 2 + 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2)
            
            # Draw replay button
            replay_button = draw_button(frame,
                                       frame.shape[1] // 2 - 150,
                                       frame.shape[0] // 2 + 100,
                                       300, 50,
                                       "PLAY AGAIN",
                                       (0, 200, 0))
            
            # Check for replay
            if index_tip and check_button_click(index_tip, replay_button):
                # Reset game
                player_score = 0
                computer_score = 0
                game_state = "MENU"
            elif cv2.waitKey(1) & 0xFF == ord('r'):
                player_score = 0
                computer_score = 0
                game_state = "MENU"
        
        # Instructions
        if game_state == "COUNTDOWN":
            cv2.putText(frame, "Show your gesture!", 
                       (50, frame.shape[0] - 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        elif game_state == "MENU":
            cv2.putText(frame, "Fist=Rock | Open=Paper | V=Scissors | Press 'S' to start", 
                       (50, frame.shape[0] - 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        else:
            cv2.putText(frame, "Press ESC to exit", 
                       (50, frame.shape[0] - 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        cv2.imshow('Rock Paper Scissors', frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == 27:  # ESC
            break
        elif key == ord('f') or key == ord('F'):  # Toggle fullscreen
            fullscreen = toggle_fullscreen('Rock Paper Scissors', fullscreen)
    
    tracker.release()
    print("\nThanks for playing!")

if __name__ == "__main__":
    main()
