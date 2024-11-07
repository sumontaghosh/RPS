import cv2
import cvzone
from cvzone.HandTrackingModule import HandDetector
import random
import streamlit as st
import time


# Initialize camera
cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

st.title("Rock Paper Scissors Game")

# Streamlit placeholders
frame_placeholder = st.empty()
stop_button = st.button("Stop")  # Button to stop the game
start_button = st.button("Start")  # Button to start the game

# Initialize Hand Detector
detector = HandDetector(maxHands=1)

# Game variables
scores = [0, 0]  # [AI, Player]
stateResult = False
imgAI = cv2.imread("Resources/1.png", cv2.IMREAD_UNCHANGED)  # Default image for imgAI
initialTime = time.time()
startGame = False  # Initially set to False
displayTime = 1  # Time to display the AI's choice in seconds
displayStartTime = 0  # Variable to keep track of when to stop displaying the AI's image

if start_button:
    startGame = True  # Start the game when the button is pressed
    initialTime = time.time()  # Reset initial time when game starts

# Game loop
while cap.isOpened():
    # Break the loop if stop button is pressed
    if stop_button:
        break

    if startGame:
        # Load background and capture frame
        imgBG = cv2.imread("Resources/BG.png")
        success, img = cap.read()
        if not success:
            st.write("Failed to capture image")
            break

        imgScaled = cv2.resize(img, (0, 0), None, 0.875, 0.875)
        imgScaled = imgScaled[:, 80:480]

        # Find hands
        hands, img = detector.findHands(imgScaled)  # with draw

        timer = time.time() - initialTime  # Time since the start of the round
        timer_display = int(timer)
        cv2.putText(imgBG, str(timer_display), (605, 435), cv2.FONT_HERSHEY_PLAIN, 6, (255, 0, 255), 4)

        if timer_display >= 3:  # After 3 seconds, determine the result
            stateResult = True
            initialTime = time.time()  # Reset initialTime for the next round

            if hands:
                playerMove = None
                hand = hands[0]
                fingers = detector.fingersUp(hand)
                if fingers == [0, 0, 0, 0, 0]:
                    playerMove = 1  # Rock
                if fingers == [1, 1, 1, 1, 1]:
                    playerMove = 2  # Paper
                if fingers == [0, 1, 1, 0, 0]:
                    playerMove = 3  # Scissors

                randomNumber = random.randint(1, 3)
                imgAI = cv2.imread(f'Resources/{randomNumber}.png', cv2.IMREAD_UNCHANGED)
                imgBG = cvzone.overlayPNG(imgBG, imgAI, (149, 310))

                # Check who wins
                if (playerMove == 1 and randomNumber == 3) or \
                        (playerMove == 2 and randomNumber == 1) or \
                        (playerMove == 3 and randomNumber == 2):
                    scores[1] += 1  # Player wins

                if (playerMove == 3 and randomNumber == 1) or \
                        (playerMove == 1 and randomNumber == 2) or \
                        (playerMove == 2 and randomNumber == 3):
                    scores[0] += 1  # AI wins

            displayStartTime = time.time()  # Record the time when we display the AI's choice

        imgBG[234:654, 795:1195] = imgScaled

        # Display imgAI only when it is defined and for the specified duration
        if stateResult:
            imgBG = cvzone.overlayPNG(imgBG, imgAI, (149, 310))
            # Check if the display time has passed
            if (time.time() - displayStartTime) < displayTime:
                stateResult = True  # Keep the state as true to keep showing the AI image
            else:
                stateResult = False  # Reset stateResult to allow the game to restart

        # Display scores
        cv2.putText(imgBG, str(scores[0]), (410, 215), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 6)
        cv2.putText(imgBG, str(scores[1]), (1112, 215), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 6)

        # Convert BGR image to RGB for Streamlit
        imgBG_rgb = cv2.cvtColor(imgBG, cv2.COLOR_BGR2RGB)

        # Update Streamlit frame placeholder
        frame_placeholder.image(imgBG_rgb, channels="RGB")

# Release resources
cap.release()
cv2.destroyAllWindows()
