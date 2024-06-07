import cv2


class camera:

    def __init__(self, controller):
        self.controller = controller
        self.cameraInputIndex = 0
        self.cv2 = cv2
        self.vid = None

    def initialize(self):
        self.cameraInputIndex = self.controller.getSettings()[
            'cameraIndex']  # this must be executed after model is initialized

    def getCameraInputIndex(self):
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
        vid = self.cv2.VideoCapture(int(index))
        isOpened = vid.isOpened()
        vid.release()
        return isOpened

    def openCamera(self):
        self.vid = self.cv2.VideoCapture(self.cameraInputIndex)

    def closeCamera(self):
        if self.vid is not None and self.vid.isOpened():
            self.vid.release()

    def isCameraOpen(self):
        if self.vid is not None and self.vid.isOpened():
            return True
        return False

    def getFrame(self):
        if self.vid is not None and self.vid.isOpened():
            ret, frame = self.vid.read()
            if ret:
                return frame
        return None
