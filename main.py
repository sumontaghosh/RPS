import random
import cv2
import cvzone
from cvzone.HandTrackingModule import HandDetector
import time
import streamlit as st
import numpy as np

# Streamlit page configuration
st.set_page_config(page_title="Rock Paper Scissors", layout="wide")

# Initialize game variables
detector = HandDetector(maxHands=1)
scores = [0, 0]  # [AI, Player]
stateResult = False
startGame = False
timer = 0

# Setup video capture
cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

# Streamlit sidebar for game start
if st.sidebar.button('Start Game'):
    startGame = True
    initialTime = time.time()
    stateResult = False

# Game logic
def process_frame():
    global timer, stateResult, scores, startGame

    success, img = cap.read()
    imgBG = cv2.imread("Resources/BG.png")
    
    imgScaled = cv2.resize(img, (0, 0), None, 0.875, 0.875)
    imgScaled = imgScaled[:, 80:480]

    hands, img = detector.findHands(imgScaled)  # with draw

    if startGame:
        if not stateResult:
            timer = time.time() - initialTime
            cv2.putText(imgBG, str(int(timer)), (605, 435), cv2.FONT_HERSHEY_PLAIN, 6, (255, 0, 255), 4)

            if timer > 3:
                stateResult = True
                timer = 0

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
                    if (playerMove == 1 and randomNumber == 3) or (playerMove == 2 and randomNumber == 1) or (playerMove == 3 and randomNumber == 2):
                        scores[1] += 1  # Player wins

                    if (playerMove == 3 and randomNumber == 1) or (playerMove == 1 and randomNumber == 2) or (playerMove == 2 and randomNumber == 3):
                        scores[0] += 1  # AI wins

    imgBG[234:654, 795:1195] = imgScaled
    if stateResult:
        imgBG = cvzone.overlayPNG(imgBG, imgAI, (149, 310))

    cv2.putText(imgBG, str(scores[0]), (410, 215), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 6)
    cv2.putText(imgBG, str(scores[1]), (1112, 215), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 6)

    return imgBG

# Display the game in Streamlit
if startGame:
    st.title("Rock Paper Scissors")
    
    # Display game frame
    imgBG = process_frame()
    
    # Convert to RGB for Streamlit
    imgBG = cv2.cvtColor(imgBG, cv2.COLOR_BGR2RGB)
    st.image(imgBG, use_column_width=True)

else:
    st.write("Press 'Start Game' from the sidebar to begin!")

