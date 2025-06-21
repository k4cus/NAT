import cv2
import os
import numpy as np
from Model import omr

class loadAnswers:

    def __init__(self, controller):
        self.controller = controller

    def initialize(self):
        self.cameraInputIndex = self.controller.getSettings()['cameraIndex']  # this must be executed after model is initialized

    def readAnswerSheet(self):
        return None

    def loadCorrectAnswersFromFile(self,currentExamName):
        with open("exams-data/" + currentExamName + "/answer_keys/answers.csv", "a+") as f:
            f.seek(0)
            ans = f.read()
        if ans == []:
            print("No answers to load. First scan the answer sheet or create the csv file manually.")
        return ans

    def loadAnswers(self, type, currentExamName, cam_index=None, file_path=None, folder_path=None):
        score_string = ""
        folders = ["/answer_keys/", "/student_answers/"]

        if cam_index is not None:
            cap = cv2.VideoCapture(cam_index)

        testing = True
        while testing:
            graded = 0
            while graded < 1:
                graded += 1
                if cam_index is not None:
                    success, img = cap.read()
                elif file_path is not None:
                    img = omr.omr.loadImageFromFile(self, file_path)

                cv2.imwrite("debugging-opencv/camera-test.png", img)
                # Sprawdź liczbę kanałów w obrazie
                if len(img.shape) == 2:  # Obraz w skali szarości
                    img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
                elif img.shape[2] == 4:  # Obraz RGBA
                    img = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)

                # Konwertuj obraz do skali szarości
                img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

                index, answers, group, page_img, images_warped, page_img_grid = omr.omr.processOneSheet(self, img)

                folders_2 = [group, index]

                if answers is not None:

                        # if currently scanning the student's answers - check if the answer keys are present
                        if type == 1:
                            if not os.path.exists("exams-data/" + currentExamName + "/answer_keys/" + str(group)):
                                os.makedirs("exams-data/" + currentExamName + "/answer_keys/" + str(group))
                            with open("exams-data/" + currentExamName + "/answer_keys/" + str(group) + "/answers.csv", "a+") as f:
                                f.seek(0)
                                ans = f.readlines()
                            if ans == []:
                                print("No answers to load. First scan the answer sheet or create the csv file manually.")
                                score_string = "Brak klucza odpowiedzi dla grupy"
                                            
                        # save the read data to files
                        
                        # create the folder to store the data
                        if not os.path.exists("exams-data/" + currentExamName + folders[type] + str(folders_2[type])):
                            os.makedirs("exams-data/" + currentExamName + folders[type] + str(folders_2[type]))
                            
                        print("\nZczytane dpowiedzi:", answers)
                        graded += 1

                        cv2.imwrite("exams-data/" + currentExamName + folders[type] + str(folders_2[type]) + "/page_processed.png", page_img_grid)
                        cv2.imwrite("exams-data/" + currentExamName + folders[type] + str(folders_2[type]) + "/page_raw.png", page_img)
                        transparent_img = np.ones((690, 490), dtype=np.uint8)
                        i = 0
                        for i in range(20):
                            txt = answers[i] + ", " + answers[i + 20] + ", " + answers[i + 40]
                            transparent_img = cv2.putText(transparent_img, txt, ((i+1)*20, 20), cv2.FONT_HERSHEY_SIMPLEX,
                                                1, (0,0,255,255), 2, cv2.LINE_AA)
                            i += 1

                        # grade if in student answers reading mode
                        if score_string != "Brak klucza odpowiedzi dla grupy":
                            if type == 1:
                                ans_list = ans[0].split(";")
                                num_questions = 60
                                score = omr.omr.score(self, ans_list[:num_questions], answers[:num_questions])
                                score_string = str(round(score[1], 2)) + "%"
                            else:
                                score_string = ""

                        # save the answers
                        with open("exams-data/" + currentExamName + folders[type] + str(folders_2[type]) + "/answers.csv", "w") as f:
                            if type == 0:
                                f.write(";".join(answers))
                            if type == 1:
                                f.write(str(index) + ";" + str(answers) + ";" + str(group) + ";" + score_string)


            testing = False # delete when you want to loop

        print("Finished scanning")
        if cam_index is not None:
            cap.release()
        if not score_string:
            score_string = ""
        if page_img_grid is None:
            page_img_grid = img
        return page_img_grid, score_string, answers, group, index