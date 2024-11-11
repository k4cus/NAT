import cv2
import os
import numpy as np
from Model import omr
import utlis


class loadAnswers:

    def __init__(self, controller):
        print("LOADING...")
        self.controller = controller
        self.omr_instance = controller.omr_instance

    def initialize(self):
        self.cameraInputIndex = self.controller.getSettings()[
            'cameraIndex']  # this must be executed after model is initialized

    def readAnswerSheet(self):
        return None

    def loadCorrectAnswersFromFile(self, currentExamName):
        with open("exams-data/" + currentExamName + "/answer_keys/answers.csv", "a+") as f:
            print("exams-data/" + currentExamName + "/answer_keys/answers.csv")
            f.seek(0)
            ans = f.read()
            print(ans)
        if ans == []:
            print("No answers to load. First scan the answer sheet or create the csv file manually.")
        return ans

    #def loadAnswers(self, type, currentExamName, cam_index=None, file_path=None, folder_path=None):
        

    # def loadAnswers(self, type, currentExamName, cam_index=None, file_path=None, folder_path=None):
    #     folders = ["/answer_keys/", "/student_answers/"]
    #
    #     if cam_index is not None:
    #         cap = cv2.VideoCapture(0)
    #
    #         if not cap.isOpened():
    #             print("Błąd: Kamera nie może zostać otwarta.")
    #             return
    #
    #         success, img = cap.read()
    #         if not success or img is None:
    #             print("Błąd: Nie udało się przechwycić obrazu z kamery.")
    #             cap.release()
    #             return
    #     else:
    #         print("Inny błąd")
    #
    #     print("TEST KAMERY POMYŚLNY")
    #     score_string = ""
    #     testing = True
    #     while testing:
    #         graded = 0
    #         while graded < 1:
    #             if cam_index is not None:
    #                 print(cam_index)
    #                 success, img = cap.read()
    #             elif file_path is not None:
    #                 img = omr.omr.loadImageFromFile(self, file_path)
    #             else:
    #                 return "Inny błąd"
    #
    #             cv2.imwrite("debugging-opencv/camera-test.png", img)
    #
    #             img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    #
    #             # print(img, "TO JEST OBRAZERK")
    #             # cv2.imshow("test", img)
    #             # cv2.waitKey(0)
    #
    #
    #
    #             print("DUPA123")
    #             #index, answers, group, page_img, images_warped, page_img_grid = self.omr_instance.processOneSheet(img)
    #             result = self.omr_instance.processOneSheet(img)
    #
    #
    #
    #             if len(result) == 5:
    #                 index, answers, group, page_img, images_warped = result
    #                 page_img_grid = None
    #             else:
    #                 index, answers, group, page_img, images_warped, page_img_grid = result
    #
    #             print(result)
    #             print("finished one page")
    #
    #
    #             folders_2 = [group, index]
    #
    #             # if answers is not None:
    #             #     print("DUPA1293Y12931283912312")
    #             #     # if currently scanning the student's answers - check if the answer keys are present
    #             #     if type == 1:
    #             #         if not os.path.exists("exams-data/" + currentExamName + "/answer_keys/" + str(group)):
    #             #             os.makedirs("exams-data/" + currentExamName + "/answer_keys/" + str(group))
    #             #         with open("exams-data/" + currentExamName + "/answer_keys/" + str(group) + "/answers.csv",
    #             #                   "a+") as f:
    #             #             f.seek(0)
    #             #             ans = f.readlines()
    #             #         if ans == []:
    #             #             print("No answers to load. First scan the answer sheet or create the csv file manually.")
    #             #             return None
    #             #
    #             #     # save the read data to files
    #             #
    #             #     # create the folder to store the data
    #             #     if not os.path.exists("exams-data/" + currentExamName + folders[type] + str(folders_2[type])):
    #             #         os.makedirs("exams-data/" + currentExamName + folders[type] + str(folders_2[type]))
    #             #
    #             #     print("\nZczytane dpowiedzi:", answers)
    #             #     graded += 1
    #             #
    #             #     # save the answers
    #             #     with open("exams-data/" + currentExamName + folders[type] + str(folders_2[type]) + "/answers.csv",
    #             #               "w") as f:
    #             #         if type == 0:
    #             #             f.write(";".join(answers))
    #             #         if type == 1:
    #             #             f.write(str(index) + ";" + str(answers) + ";" + str(group))
    #             #
    #             #     cv2.imwrite(
    #             #         "exams-data/" + currentExamName + folders[type] + str(folders_2[type]) + "/page_img_" + str(
    #             #             graded) + ".png", page_img)
    #             #     for im in range(len(images_warped)):
    #             #         cv2.imwrite("exams-data/" + currentExamName + folders[type] + str(
    #             #             folders_2[type]) + "/answers_grid_" + str(im) + ".png", images_warped[im])
    #             #     cv2.imwrite(
    #             #         "exams-data/" + currentExamName + folders[type] + str(
    #             #             folders_2[type]) + "/answers_grid_all" + str(
    #             #             graded) + ".png", cv2.hconcat(images_warped))
    #             #     transparent_img = np.ones((690, 490), dtype=np.uint8)
    #             #     i = 0
    #             #     for i in range(20):
    #             #         txt = answers[i] + ", " + answers[i + 20] + ", " + answers[i + 40]
    #             #         transparent_img = cv2.putText(transparent_img, txt, ((i + 1) * 20, 20),
    #             #                                       cv2.FONT_HERSHEY_SIMPLEX,
    #             #                                       1, (0, 0, 255, 255), 2, cv2.LINE_AA)
    #             #         i += 1
    #             #
    #             #     # grade if in student answers reading mode
    #             #     if type == 1:
    #             #         ans_list = ans[0].split(";")
    #             #         print(ans_list)
    #             #         print(answers)
    #             #         num_questions = 55
    #             #         score = omr.omr.score(self, ans_list[:num_questions], answers[:num_questions])
    #             #         print("Wynik: " + str(round(score[1], 2)) + "%")
    #             #         cv2.imwrite(
    #             #             "exams-data/" + currentExamName + "/student_answers/" + str(index) + "/result_img.png",
    #             #             transparent_img)
    #             #         score_string = str(round(score[1], 2)) + "%"
    #             #     else:
    #             #         score_string = "" #funkcja
    #             break
    #         testing = False  # delete when you want to loop
    #
    #
    #     print("Finished scanning")
    #     if cam_index is not None:
    #         cap.release()
    #
    #     print(score_string)
    #     return page_img_grid, score_string