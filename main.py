import cv2
import cvzone
from cvzone.HandTrackingModule import HandDetector
import random
import streamlit as st
import time

# Set up Streamlit session state for the game start flag
if 'game_started' not in st.session_state:
    st.session_state.game_started = False

# Streamlit placeholders
frame_placeholder = st.empty()
stop_button = st.button("Stop")
start_button = st.button("Start")

# Initialize Hand Detector
detector = HandDetector(maxHands=1)

# Game variables
scores = [0, 0]  # [AI, Player]
stateResult = False
initialTime = time.time()
displayTime = 1  # Time to display the AI's choice in seconds
displayStartTime = 0

# Load images with error handling
def load_image(image_path):
    img = cv2.imread(image_path)
    if img is None:
        st.error(f"Error loading image: {image_path}")
        return np.zeros((480, 640, 3), dtype=np.uint8)  # Return a black placeholder image if not found
    return img

# Load necessary images for the game
imgBG = load_image("Resources/BG.png")
imgAI = load_image("Resources/1.png")

# Handle the game start and session state
if start_button:
    st.session_state.game_started = True
    initialTime = time.time()

# Only run the game loop if the game has started
if st.session_state.game_started:
    while True:
        # Break the loop if stop button is pressed
        if stop_button:
            st.session_state.game_started = False
            break

        # Simulate the player image (use BG.png or any other image as placeholder for now)
        img = imgBG  # You can use the background image as a placeholder for now

        # Resize and crop the image
        imgScaled = cv2.resize(img, (0, 0), None, 0.875, 0.875)
        imgScaled = imgScaled[:, 80:480]

        # Find hands
        hands, img = detector.findHands(imgScaled)  # Detect hands in placeholder image

        # Game timer logic
        timer = time.time() - initialTime
        timer_display = int(timer)
        cv2.putText(imgBG, str(timer_display), (605, 435), cv2.FONT_HERSHEY_PLAIN, 6, (255, 0, 255), 4)

        if timer_display >= 3:
            stateResult = True
            initialTime = time.time()

            if hands:
                playerMove = None
                hand = hands[0]
                fingers = detector.fingersUp(hand)
                if fingers == [0, 0, 0, 0, 0]:
                    playerMove = 1  # Rock
                elif fingers == [1, 1, 1, 1, 1]:
                    playerMove = 2  # Paper
                elif fingers == [0, 1, 1, 0, 0]:
                    playerMove = 3  # Scissors

                randomNumber = random.randint(1, 3)
                imgAI = load_image(f"Resources/{randomNumber}.png")
                imgBG = cvzone.overlayPNG(imgBG, imgAI, (149, 310))

                # Determine the winner
                if (playerMove == 1 and randomNumber == 3) or \
                        (playerMove == 2 and randomNumber == 1) or \
                        (playerMove == 3 and randomNumber == 2):
                    scores[1] += 1  # Player wins

                if (playerMove == 3 and randomNumber == 1) or \
                        (playerMove == 1 and randomNumber == 2) or \
                        (playerMove == 2 and randomNumber == 3):
                    scores[0] += 1  # AI wins

            displayStartTime = time.time()

        imgBG[234:654, 795:1195] = imgScaled

        # Display imgAI only for the specified duration
        if stateResult:
            imgBG = cvzone.overlayPNG(imgBG, imgAI, (149, 310))
            if (time.time() - displayStartTime) < displayTime:
                stateResult = True
            else:
                stateResult = False

        # Display scores
        cv2.putText(imgBG, str(scores[0]), (410, 215), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 6)
        cv2.putText(imgBG, str(scores[1]), (1112, 215), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 6)

        # Convert BGR image to RGB for Streamlit
        imgBG_rgb = cv2.cvtColor(imgBG, cv2.COLOR_BGR2RGB)

        # Update Streamlit frame placeholder
        frame_placeholder.image(imgBG_rgb, channels="RGB")
