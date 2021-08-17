"""This demo is made by Teukkaniikka

Support me for more codes & comments:
- Patreon: https://www.patreon.com/teukkaniikka
- PayPal: paypal.me/Teukkaniikka
"""

import cv2
import mediapipe as mp
import pyautogui
import time

# Hand tracking stuff
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
drawing_styles = mp.solutions.drawing_styles

# Keep track of the character being presed
char = None

# Is a key pressed
pressed = False

# When did the keypress start
startTime = None

# Did we already press the key? (don't hold it down, just stroke
# it once)
sentChar = False

# For webcam input:
cap = cv2.VideoCapture(0)

# Put the camera resolution and scaling factor here
# Just set it to 1 if you don't want to up-/downscale it
camera_width = 640
camera_height = 480
scale = 2

img_width = int(camera_width*scale)
img_height = int(camera_height*scale)

with mp_hands.Hands(
        max_num_hands=2,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5) as hands:
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            # If loading a video, use 'break' instead of 'continue'.
            continue

        # Flip the image horizontally for a later selfie-view display, and convert
        # the BGR image to RGB.
        image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
        image = cv2.resize(image, (img_width, img_height))
        
        # To improve performance, optionally mark the image as not writeable to
        # pass by reference.
        image.flags.writeable = False
        results = hands.process(image)

        # Draw the hand annotations on the image.
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(
                    image, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                    drawing_styles.get_default_hand_landmark_style(),
                    drawing_styles.get_default_hand_connection_style())

                # Find the markers for the index finger and thumb, calculate the distance,
                # convert it to brightness and sent it to the Arduino
                try:
                    # NOTE: https://google.github.io/mediapipe/solutions/hands#python-solution-api
                    listOfMarks = hand_landmarks.landmark

                    #p2 = IDNEX_FINGER_TIP
                    p2 = listOfMarks[8]

                    # How far the index finger's tip is from the camera if we look only from the z-axis
                    distance = abs(p2.z)

                    # If it's close enough
                    if distance > 0.1:
                        
                        # Calculate the position on the grid and
                        # map the character according to the grid
                        x = int(p2.x*10)
                        y = int(p2.y*3)

                        # The grid starts from 0, but the letter A is actually 65 in decimal
                        # so we need to add it there
                        # NOTE: https://www.asciitable.com/
                        char = chr(65+x+y*10)

                        # If this was the first time we pressed a key, start a timer
                        if not pressed:
                            startTime = time.time()
                            pressed = True
                        else:
                            # If the key has been pressed for 0.1 seconds and we haven't made a keystroke
                            if time.time() - startTime > 0.1 and not sentChar:

                                # These are for the last characters, because I wanted to add some
                                # function keys like backspace and enter.
                                #
                                # Why this is done?
                                # ASCII characters that come after Z are [\]^_` and we don't need those
                                if ord(char) == 91:
                                    pyautogui.press('backspace')
                                elif ord(char) == 92:
                                    pyautogui.press('enter')
                                elif ord(char) == 93:
                                    pyautogui.press('tab')
                                elif ord(char) == 94:
                                    pyautogui.press('space')
                                else:
                                    pyautogui.press(char)

                                # And put the sentChar to True, we don't want to hold the key down
                                sentChar = True

                    # Reset all after we stopped pressing the keyboard
                    else:
                        pressed = False
                        char = None
                        sentChar = False

                # If the markers weren't found (this is probably not needed idk)        
                except Exception as e:
                    print(e)

        # Draw the grid
        for x in range(0, img_width, int(img_width/10)):
            cv2.line(image, (x, 0), (x, img_height), (0, 255, 255), 2, 1)
        for y in range(0, img_height, int(img_height/3)):
            cv2.line(image, (0, y), (img_width, y), (0, 180, 255), 2, 1)

        # Draw the characters
        font = cv2.FONT_HERSHEY_SIMPLEX
        fontScale = 1
        for x in range(0, 10):
            for y in range(0, 3):
                character = chr(65+x+y*10)

                if character == char:
                    color = (0,255,0)
                else:
                    color = (255, 100, 0)

                if ord(character) == 91:
                    character = "<"
                if ord(character) == 92:
                    character = ">"
                if ord(character) == 93:
                    character = "T"
                if ord(character) == 94:
                    character = "_"

                image = cv2.putText(image,
                                    character,
                                    (x*int(img_width/10)+int(img_width/20),
                                    y*int(img_height/3)+int(img_height/6)),
                                    font,
                                    fontScale,
                                    color,
                                    2,
                                    cv2.LINE_AA
                                    )

        # Show the image
        cv2.imshow('KeyboardDemo', image)

        # Press <Q> to exit
        if cv2.waitKey(1) & 0xFF == 113:
            break

# Let the camera be free!
cap.release()
