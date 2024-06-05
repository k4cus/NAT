import cv2


class camera:

    def __init__(self, controller):
        self.controller = controller
        self.cameraInputIndex = 0

    def initialize(self):
        self.cameraInputIndex = self.controller.getSettings()['cameraIndex']

    def getCameraInputIndex(self):
        print("get " + str(self.cameraInputIndex))
        return self.cameraInputIndex

    def setCameraInputIndex(self, index):
        # check if input is valid
        isInputValid = self.checkCameraIndex(index)
        if isInputValid:
            self.cameraInputIndex = index
            self.controller.setSetting('cameraIndex', int(index))
        return isInputValid  # message to display in view

    def checkCameraIndex(self, index):
        # check if camera index is valid
        vid = cv2.VideoCapture(int(index))
        isOpened = vid.isOpened()
        vid.release()
        return isOpened
