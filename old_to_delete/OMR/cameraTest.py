from time import sleep

import cv2
import keyboard

exitProgram = False


def quitProgram():
    global exitProgram
    exitProgram = True


# set hotkey
keyboard.add_hotkey('q', lambda: quitProgram())


def checkAvaliableCameras():
    camera_index = []
    for i in range(2):
        print(i)
        vid = cv2.VideoCapture(i)
        print("isOpened: ", vid.isOpened())
        ret, frame = vid.read()
        vid.release()
        if ret:
            camera_index.append(i)
    return camera_index


indexes = checkAvaliableCameras()
print("Available cameras: ", indexes)

cap = cv2.VideoCapture(0)
cap.set(10, 160)
success, img = cap.read()
# cv2.startWindowThread()
# cv2.namedWindow("Image from camera")
# cv2.imshow("Image from camera", img)
# cv2.waitKey(1)
while not exitProgram:
    success, img = cap.read()
    if success:
        cv2.imshow("Image from camera", img)
        cv2.waitKey(1)

# After the loop release the cap object
cap.release()
# Destroy all the windows
cv2.destroyAllWindows()
