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

    def loadCorrectAnswersFromFile(self):
        currentExamName = "nazwa_egzaminu_on_2024-06-06_at_20-52"
        with open("exams-data/" + currentExamName + "/answer_keys/answers.csv", "r") as f:
            ans = f.readlines()
        if ans == []:
            print("No answers to load. First scan the answer sheet")
        return ans

    def loadAnswers(self, type):
        currentExamName = "nazwa_egzaminu_on_2024-06-05_at_21-34" # TODO
        path_to_image = "data/answer_sheets/answer_sheet_5_3.png"
        cap = cv2.VideoCapture(0)
        cap.set(10, 160)
        img = omr.load_image(path_to_image, False)
        testing = True
        while testing:
            #success, img = cap.read()
            #cv2.imwrite("debugging-opencv/camera-test.png", img)
            #img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            graded = False
            while graded == False:
                if type == 0: # Only scan correct answers
                    _, answers, group_answers = omr.omr_read_correct_answers(img)
                    print("\nPoprawne odpowiedzi:", answers)
                    if answers is not None:
                        graded = True
                        with open("exams-data/" + currentExamName + "/answer_keys/answers.csv", "w") as f:
                            f.write(";".join(answers))
                if type == 1: # Load correct answers + scan student's answers
                    _, answers, group_answers = omr.omr_read_correct_answers(img)
                    print("\nPoprawne odpowiedzi:", answers)

                    index, score, group = omr.omr_grade(answers, img)
                    print("\nIndeks:", index, "\nWynik:", score, "\nGrupa:", group)
                    if answers is not None and score is not None:
                        graded = True
                        with open("exams-data/" + currentExamName + "/student_answers/answers.csv", "w") as f:
                            f.write(str(index) + ";" + str(score) + ";" + str(group))


        return None