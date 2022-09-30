import math
import cv2
import mediapipe as mp
import random
import time

def get_computer_move():
    return random.choice(["rock", "paper", "scissors"])

def get_winner(user=None, comp=None):
    if user is None or comp is None:
        assert Exception("ERROR: Enter user and computer moves")

    if user==comp:
        return "draw"
    elif user=="rock" and comp=="paper":
        return "computer wins"
    elif user=="rock" and comp=="scissors":
        return "user wins"
    elif user=="paper" and comp=="scissors":
        return "computer wins"
    elif user=="paper" and comp=="rock":
        return "user wins"
    elif user=="scissors" and comp=="rock":
        return "computer wins"
    elif user=="scissors" and comp=="paper":
        return "user wins"
    else:
        return "wtffff"

def get_distance(x1, y1, x2, y2):
    x_distance = x1 - x2
    y_distance = y1 - y2
    distance = math.sqrt((x_distance ** 2) + (y_distance ** 2))
    return distance

def display_text(string, pos, image, font_scale=1):
    font = cv2.FONT_HERSHEY_SIMPLEX
    image = cv2.flip(image, 1) # flip the img and un flip to display text correctly 
    cv2.putText(image, string, pos, font, font_scale, (0,0,255), 2, cv2.LINE_AA)
    image = cv2.flip(image, 1)
    return image

def rescale_frame(frame, percent=75):
    width = int(frame.shape[1] * percent/ 100)
    height = int(frame.shape[0] * percent/ 100)
    dim = (width, height)
    return cv2.resize(frame, dim, interpolation =cv2.INTER_AREA)

def main_loop():
    mp_drawing = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles
    mp_hands = mp.solutions.hands

    cap = cv2.VideoCapture(0)
    window_name = "Rock Paper Scissors"
    user_move = ""
    prev_user_move = ""
    move_count_down = 3
    show_moves = False
    show_moves_timer = time.time()
    move_timer = time.time()
    move_timer_temp = time.time()

    with mp_hands.Hands(
        model_complexity=0,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
        max_num_hands=1) as hands:
            while cap.isOpened():
                success, image = cap.read()
                image = rescale_frame(image, percent=120)
                if not success:
                    print("Ignoring empty camera frame.")
                    continue

                # To improve performance, optionally mark the image as not writeable to
                # pass by reference.
                image.flags.writeable = False
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                results = hands.process(image)

                image.flags.writeable = True
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)


                # Draw the hand annotations on the image.
                if results.multi_hand_landmarks and not show_moves:
                    for hand_landmarks in results.multi_hand_landmarks:
                        mp_drawing.draw_landmarks(
                            image,
                            hand_landmarks,
                            mp_hands.HAND_CONNECTIONS,
                            mp_drawing_styles.get_default_hand_landmarks_style(),
                            mp_drawing_styles.get_default_hand_connections_style())

                    # analyzing user's move 
                    index_tip_coords = results.multi_hand_landmarks[0].landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                    index_dip_coords = results.multi_hand_landmarks[0].landmark[mp_hands.HandLandmark.INDEX_FINGER_DIP]
                    middle_tip_coords = results.multi_hand_landmarks[0].landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
                    middle_dip_coords = results.multi_hand_landmarks[0].landmark[mp_hands.HandLandmark.MIDDLE_FINGER_DIP]
                    ring_tip_coords = results.multi_hand_landmarks[0].landmark[mp_hands.HandLandmark.RING_FINGER_TIP]
                    ring_dip_coords = results.multi_hand_landmarks[0].landmark[mp_hands.HandLandmark.RING_FINGER_DIP]

                    if (index_tip_coords.y < index_dip_coords.y and middle_tip_coords.y < middle_dip_coords.y and ring_tip_coords.y < ring_dip_coords.y): # paper
                        prev_user_move = user_move
                        user_move = "paper"
                    elif (index_tip_coords.y < index_dip_coords.y and middle_tip_coords.y < middle_dip_coords.y): # scissors
                            prev_user_move = user_move
                            user_move = "scissors"
                    else: # rock
                        prev_user_move = user_move
                        user_move = "rock" 

                    if prev_user_move == user_move:
                        if time.time() - move_timer > 3:
                            show_moves = True
                            computer_move = get_computer_move()
                            show_moves_timer = time.time()
                            move_timer = time.time()
                        if time.time() - move_timer_temp >= 1:
                            move_count_down -= 1
                            move_timer_temp = time.time()
                    else:
                        move_timer_temp = time.time()
                        move_timer = time.time()
                        move_count_down = 3

                elif show_moves:
                    image = display_text(f"user moved {user_move}", (20, 100), image, font_scale=1.5)
                    image = display_text(f"computer moved {computer_move}", (20, 140), image, font_scale=1.5)
                    image = display_text(f"{get_winner(user=user_move, comp=computer_move)}", (20, 180), image, font_scale=1.5)
                    if time.time() - show_moves_timer > 5:
                        show_moves = False
                        move_timer = time.time()
                        move_count_down = 3
                        move_timer_temp = time.time()
                        user_move = "null"
                else:
                    move_timer = time.time()
                    move_count_down = 3
                    move_timer_temp = time.time()
                    user_move = "null"
                
                image = display_text(f"user: {user_move} | timer: {move_count_down}", (18, 23), image) # edits img and gives it back
                cv2.imshow(window_name, cv2.flip(image, 1)) # Flip the image horizontally for a selfie-view
                if cv2.waitKey(5) & 0xFF == 27 or (cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1): # esc key or x btn to quit
                    break
    cap.release()

if __name__=="__main__":
    main_loop()
