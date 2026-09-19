from warnings import catch_warnings

import cv2 as cv
import numpy as np
import time
import smtplib
from email.mime.text import MIMEText
import os
# from playsound import playsound
from twisted.words.xish.domish import elementStream
from pydub import AudioSegment
from pydub.playback import play

# from send_sms_script import send_message
from send_email_script import send_email
from fall_detection.detectfall import fall_main  # Import fall detection
from hand_gesture.app import gesture_main
# Import gesture detection
from fall_detection.detectfall import predictions


# Initialize flags and arrays
flgFall = False
flgThumbsUp = False
flgThumbsDown = False
arrFall = [0] * 60
arrThumbsUp = [0] * 60
arrThumbsDown = [0] * 60
i = 0
j = 0
fallTime = None
# import os
# os.environ["CUDA_VISIBLE_DEVICES"]="-1"


# Initialize email flag for testing
SEND_EMAIL = True # Set to False to test without actually sending email

try:
    cap = cv.VideoCapture(0)
    while True:
        # Capture camera feed
        # cap = cv.VideoCapture(0)

        ret, frame = cap.read()

        frame = cv.resize(frame, (640, 480))  # Resize to lower resolution #24 dec

        # Display the video feed during testing. comment later
        cv.imshow("Camera Feed", frame) #19 DEC

        if not ret:
            print("Error capturing frame.")
            break

        # FALL DETECTION LOGIC
        if not flgFall:
            fall_detected = fall_main(frame)  # Pass the current frame to fall_main
              # Assuming predictions is accessible here

            # Correctly update the circular buffer: Overwrite with 1 if fall detected, 0 otherwise
            if fall_detected == 0:  # predict = 0 > Fall > assign 1, predict = 1 > no fall > assign 0
                arrFall[i] = 1
            else:
                arrFall[i] = 0

            # Move to the next index in the circular buffer
            i = (i + 1) % 60

            # Debugging information
            print(f"Buffer: {arrFall}")
            print(f"Falls in last 60 frames: {sum(arrFall)}")

            # Count falls in the last 60
            countFall = sum(arrFall)

            # Trigger fall action if falls detected in 80% of frames
            if countFall >= 48:
                flgFall = True
                song = AudioSegment.from_wav("/home/divya/PycharmProjects/SmartSentinel/confirming.wav")
                play(song)
                # print("Are you okay? show thumbs up")
                # playsound("/home/divya/Downloads/confirming.mp3")
                fallTime = time.time()  # Record fall time

                # Reset gesture arrays
                arrThumbsUp = [0] * 60
                arrThumbsDown = [0] * 60
            # End of countFall >-48
        # End of flgFall

        # GESTURE DETECTION LOGIC
        # Call gesture_main() to predict gesture
        gesture= gesture_main(frame)  # Thumbs Up, Thumbs Down, Other - Ignore

        # Correctly update the circular buffer: Overwrite with 1 if fall detected, 0 otherwise
        if gesture == "Thumbs Up":
            arrThumbsUp[j] = 1
            arrThumbsDown[j] = 0
        elif gesture == "Thumbs Down":
            arrThumbsUp[j] = 0
            arrThumbsDown[j] = 1
        else:
            arrThumbsUp[j] = 0
            arrThumbsDown[j] = 0

        # Move to the next index in the circular buffer
        j = (j + 1) % 60

        print(f"Buffer_ThumbsUp: {arrThumbsUp}")
        print(f"ThumbsUp in last 60 frames: {sum(arrThumbsUp)}")
        print(f"Buffer_ThumbsDown: {arrThumbsDown}")
        print(f"ThumbsUp in last 60 frames: {sum(arrThumbsDown)}")

        # Count gestures in the last 60 frames
        countThumbsUp = sum(arrThumbsUp)
        countThumbsDown = sum(arrThumbsDown)

        # Check if thumbs-up or  thumbs-down gesture detected
        if countThumbsUp >= 20:
            flgThumbsUp = True
            flgThumbsDown = False
            flgFall = False  # Reset fall flag
        elif countThumbsDown >= 30:
            flgThumbsUp = False
            flgThumbsDown = True
            flgFall = True # set fall flag
        else:
            flgThumbsUp = False
            flgThumbsDown = False

        # End of countFall >-48

        # Action on thumbs-down or timeout
        if flgThumbsDown or (fallTime is not None and (time.time() - fallTime) > 2):
            song = AudioSegment.from_wav("/home/divya/PycharmProjects/SmartSentinel/sendinghelp.wav")
            play(song)
            # print("help is on the way. hold on")
            # playsound("/home/divya/Downloads/sendinghelp.mp3")  # Play sound
            #Email logic 27 Dec 2024
            print("Sending email to authorities...")
            if SEND_EMAIL:
                send_email()
            else:
                print("Email would be sent (testing mode).")
            #End email logic
            flgThumbsUp = False
            flgThumbsDown = True
        # End if

        # Action on thumbs-up
        if flgThumbsUp:
            song = AudioSegment.from_wav("/home/divya/PycharmProjects/SmartSentinel/ignoring.wav")
            play(song)
            # print("all okay then take care")
            # playsound("/home/divya/Downloads/ignoring.mp3")  # Play thumbs-up sound
            print("User acknowledged as OK.")
        #  End if

        # Reset flags and wait logic
        if flgThumbsUp or flgThumbsDown:
            flgFall = False
            fallTime = None
            flgThumbsUp = False
            flgThumbsDown = False
            arrFall = [0] * 60
            arrThumbsUp = [0] * 60
            arrThumbsDown = [0] * 60


            print("Waiting for 15 minutes before resuming...")
            time.sleep(0.01)  # 10 ms delay #24 dec

            # time.sleep(30)  # Wait for 2 minutes (120 seconds)
        #End if

        # Key capture code
        # if cv.waitKey(1) & 0xFF == ord('q'):  # Exit on pressing 'q'
        #     print("Exiting...")
        #     break

   # End of while loop

    # To Do: add keystroke capture in end of while and if key pressed is q then break
    cap.release()
    cv.destroyAllWindows()
    # except KeyboardInterrupt:
    # print("Exiting gracefully...")

except Exception as e:
    print("An exception occurred...")
    print(e)

finally:
    print("finally...")
