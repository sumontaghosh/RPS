import cv2
import cvzone
from cvzone.HandTrackingModule import HandDetector
import random
import streamlit as st
import time

# Initialize session state for game control
if "game_started" not in st.session_state:
    st.session_state.game_started = False
if "scores" not in st.session_state:
    st.session_state.scores = [0, 0]  # [AI, Player]

# Title and buttons
st.title("Rock Paper Scissors Game")
start_button = st.button("Start")
stop_button = st.button("Stop")

# Hand Detector
detector = HandDetector(maxHands=1)

# Game control logic
if start_button:
    st.session_state.game_started = True
    initial_time = time.time()  # Start round timer

if stop_button:
    st.session_state.game_started = False

# Main game display logic
frame_placeholder = st.empty()

if st.session_state.game_started:
    imgBG = cv2.imread("Resources/BG.png")
    img = cv2.imread("Resources")

    if img is None or imgBG is None:
        st.error("Error loading game resources. Please check the file paths.")
    else:
        # Resize and overlay player image
        img_scaled = cv2.resize(img, (0, 0), None, 0.875, 0.875)
        img_scaled = img_scaled[:, 80:480]
        imgBG[234:654, 795:1195] = img_scaled

        # Hand detection
        hands, img_processed = detector.findHands(img_scaled, flipType=False)

        # Timer display
        timer_display = int(time.time() - initial_time)
        cv2.putText(imgBG, str(timer_display), (605, 435), cv2.FONT_HERSHEY_PLAIN, 6, (255, 0, 255), 4)

        if timer_display >= 3:
            if hands:
                player_move = None
                hand = hands[0]
                fingers = detector.fingersUp(hand)

                # Determine player's move
                if fingers == [0, 0, 0, 0, 0]:
                    player_move = 1  # Rock
                elif fingers == [1, 1, 1, 1, 1]:
                    player_move = 2  # Paper
                elif fingers == [0, 1, 1, 0, 0]:
                    player_move = 3  # Scissors

                # Random AI move
                ai_move = random.randint(1, 3)
                imgAI = cv2.imread(f'Resources/{ai_move}.png', cv2.IMREAD_UNCHANGED)
                imgBG = cvzone.overlayPNG(imgBG, imgAI, (149, 310))

                # Scoring logic
                if (player_move == 1 and ai_move == 3) or \
                        (player_move == 2 and ai_move == 1) or \
                        (player_move == 3 and ai_move == 2):
                    st.session_state.scores[1] += 1  # Player scores
                elif (player_move == 3 and ai_move == 1) or \
                        (player_move == 1 and ai_move == 2) or \
                        (player_move == 2 and ai_move == 3):
                    st.session_state.scores[0] += 1  # AI scores

                # Restart timer
                initial_time = time.time()

        # Score display
        cv2.putText(imgBG, str(st.session_state.scores[0]), (410, 215), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 6)
        cv2.putText(imgBG, str(st.session_state.scores[1]), (1112, 215), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 6)

        # Convert to RGB and display in Streamlit
        imgBG_rgb = cv2.cvtColor(imgBG, cv2.COLOR_BGR2RGB)
        frame_placeholder.image(imgBG_rgb, channels="RGB")

