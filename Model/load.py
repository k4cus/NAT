import cv2
import sys
import os
sys.path.append("..")
from OMR import OMR_main as omr

class loadAnswers:

    def __init__(self, controller):
        print("LOADING...")
        self.controller = controller

    def initialize(self):
        self.cameraInputIndex = self.controller.getSettings()['cameraIndex']  # this must be executed after model is initialized

    def readAnswerSheet(self):
        return None

    def loadCorrectAnswersFromFile(self,currentExamName):
        with open("exams-data/" + currentExamName + "/answer_keys/answers.csv", "a+") as f:
            ans = f.readlines()
        if ans == []:
            print("No answers to load. First scan the answer sheet or create the csv file manually.")
        return ans

    def loadAnswers(self, type, currentExamName):
        path_to_image = "data/answer_sheets/answer_sheet_5_8.jpg"
        cap = cv2.VideoCapture("http://192.168.1.108:4747/video?640x480")
        cap.set(10, 160)
        #img = omr.load_image(path_to_image, False)
        testing = True
        while testing:
            success, img = cap.read()
            cv2.imwrite("debugging-opencv/camera-test.png", img)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            graded = False
            if graded == False:
                if type == 0: # Only scan correct answers
                    _, answers, group_answers, page_img = omr.omr_read_correct_answers(img)
                    print("\nPoprawne odpowiedzi:", answers)
                    if answers is not None:
                        graded = True
                        with open("exams-data/" + currentExamName + "/answer_keys/answers.csv", "w") as f:
                            f.write(";".join(answers))

                        cv2.imwrite("exams-data/" + currentExamName + "/student_answers/page_img.png", page_img)

                if type == 1: # Load correct answers + scan student's answers
                    _, answers, group_answers, page_img = omr.omr_read_correct_answers(img)
                    print("\nPoprawne odpowiedzi:", answers)

                    index, score, group = omr.omr_grade(answers, img)
                    if index is not None:
                        print("\nIndeks:", index, "\nWynik:", score, "\nGrupa:", group)
                    if answers is not None and score is not None:
                        graded = True
                        with open("exams-data/" + currentExamName + "/student_answers/answers.csv", "w") as f:
                            f.write(str(index) + ";" + str(score) + ";" + str(group))

            #testing = False # delete when you want loop


        return None