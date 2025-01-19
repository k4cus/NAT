import os
import random
import threading
import time
import numpy as np
import base64
import time
from pynput import mouse

import cv2

from Model.camera import camera
from Model.config import examsFolder, directories
from Model.examData import examData
from Model.omr import omr
from Model.storage import storage
from Model.load import loadAnswers


class mainModel:

    def __init__(self, controller):
        self.storage = storage(controller)
        self.controller = controller
        self.omr = omr(self.controller)
        self.data = None
        self.camera = camera(self.controller)
        self.loadAnswers = loadAnswers
        self.image = None
        self.clicks = 0
        self.coords = []

        self.readFromFileExtensions = ["pdf", "png", "jpg"]

    def createNewExam(self, name):
        print("MODEL - Tworzę nowy folder z egzaminem o nazwie: " + name)
        # create folders
        if not os.path.exists(examsFolder):
            os.makedirs(examsFolder)
        folderCreateDate = time.strftime("%Y-%m-%d_at_%H-%M")
        examFolder = examsFolder + "/" + name + "_on_" + folderCreateDate + "/"

        if os.path.exists(examFolder):
            version = 2
            while os.path.exists(examFolder[:-1] + "_v" + str(version) + "/"):
                version += 1
            examFolder = examFolder[:-1] + "_v" + str(version) + "/"

        os.makedirs(examFolder)
        for folder in directories:
            if not os.path.exists(examFolder + folder):
                os.makedirs(examFolder + folder)

        # store information about which exam is open currently
        self.data = examData(examFolder)
        self.notifyObservers()

    def openExistingExam(self, name):
        folderToOpen = examsFolder + "/" + name + "/"
        if os.path.exists(folderToOpen):
            print("MODEL - Otwieram folder z egzaminem o nazwie: " + name)
            self.data = examData(folderToOpen)
        else:
            print("MODEL - Nie ma takiego folderu z egzaminem: " + name)
        self.notifyObservers()

    def getExamName(self):
        if self.data is not None:
            return self.data.getExamName()
        return None

    def notifyObservers(self):
        self.controller.UpdateView()

    def getExamsList(self):
        folderList = []
        for item in os.listdir(examsFolder):
            if os.path.isdir(os.path.join(examsFolder, item)):
                folderList.append(item)
        folderList.sort(reverse=True)  # newest exams on top
        return folderList

    '''
    def enterKeysReadingMode(self, exam_name):
        self.camera.openCamera()
        if self.camera.isCameraOpen():
            for i in range(10):
                img = self.camera.getFrame()
                # cv2.imshow("Sheep", img)
                # cv2.waitKey(1)

                print(img)
        self.camera.closeCamera()
        # cv2.destroyAllWindows()
        # here we need to process the image and store good results in mainModel
        print("MODEL - Entering keys reading mode")
        pass  # start reading keys from camera
        '''

    def enterKeysReadingMode(self, exam_name):
        print("MODEL - Entering answers reading mode")
        cam_index = self.camera.getCameraInputIndex()
        self.loadAnswers.loadAnswers(self, 0, exam_name, cam_index)
        pass

    def enterAnswersReadingMode(self, exam_name):
        print("MODEL - Entering answers reading mode")
        cam_index = self.camera.getCameraInputIndex()
        self.loadAnswers.loadAnswers(self, 1, exam_name, cam_index)
        pass  # start reading exam from camera

    def readKeysFromFile(self, filePathList, exam_name):
        print("MODEL - Reading keys from file")
        print("filePathList: ", filePathList)

        for file in filePathList:
            img = self.loadAnswers.loadAnswers(self, 0, exam_name, file_path=file)
        return img


    def readAnswersFromFile(self, filePathList, exam_name):
        print("MODEL - Reading answers from file")
        print("filePathList: ", filePathList)

        for file in filePathList:
            img = self.loadAnswers.loadAnswers(self, 1, exam_name, file_path=file)
        return img

    def getResultsImgPath(self, exam_name):
        r = str("../exams-data/" + exam_name + "/student_answers/")  # TODO
        return r

    def pageFinder(self, image):
        self.clicks = 0
        self.coords = []

        with mouse.Listener(on_click=self.on_click) as listener:
            try:
                listener.join()
            except:
                pass
        print(self.coords)

        image = base64.b64decode(image)
        #print(image)
        image = np.frombuffer(image, np.uint8)

        # Decode the numpy array to an image
        image = cv2.imdecode(image, cv2.IMREAD_GRAYSCALE)
        res = self.omr.processOneSheet(image, cropped=True, coords=self.coords)[5]
        cv2.imwrite("debugging-opencv/new_img.png", res)
        return (res)


    def on_click(self, x, y, button, pressed):
        #print(x, y, self.clicks)
        if self.clicks % 2 == 0:
            self.coords.append([x,y])
        self.clicks = self.clicks + 1
        if (self.clicks>=7):
            raise Exception("Too many clicks")

