import cv2


class camera:

    def __init__(self):
        self.cameraInputIndex = 0


    def getCameraInputIndex(self):
        print("get " + str(self.cameraInputIndex))
        return self.cameraInputIndex

    def setCameraInputIndex(self, index):
        # check if input is valid
        isInputValid = self.checkCameraIndex(index)
        if isInputValid:
            self.cameraInputIndex = index
            print("set " + str(self.cameraInputIndex))
        return isInputValid  # message to display in view

    def checkCameraIndex(self, index):
        # check if camera index is valid
        vid = cv2.VideoCapture(index)
        print(vid.isOpened())
        print("check camera: " + str(index))
        success, img = vid.read()
        cv2.waitKey(1)
        vid.release()
        return success
