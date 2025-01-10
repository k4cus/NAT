import cv2
import os
import numpy as np
from Model import omr
import subprocess

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
            print("exams-data/" + currentExamName + "/answer_keys/answers.csv")
            f.seek(0)
            ans = f.read()
            print(ans)
        if ans == []:
            print("No answers to load. First scan the answer sheet or create the csv file manually.")
        return ans

    def loadAnswers(self, type, currentExamName, cam_index=None, file_path=None, folder_path=None):
        folders = ["/answer_keys/", "/student_answers/"]

        if cam_index is not None:
            camera_index = 'Microsoft® LifeCam HD-5000'  # Zmień na nazwę swojej kamerki (ffmpeg -list_devices true -f dshow -i dummy)
            video_size = "640x480"  # Rozdzielczość obrazu
            fps = 30  # Liczba klatek na sekundę

            command = [
                "ffmpeg",
                "-f", "dshow",  # Format dla Windowsa
                "-framerate", str(fps),
                "-video_size", video_size,
                "-i", f"video={camera_index}",  # Kamerka
                "-pix_fmt", "bgr24",  # Format obrazu zgodny z OpenCV
                "-f", "rawvideo",  # Surowy format wideo
                "-"
            ]
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, bufsize=10 ** 8)
        testing = True
        while testing:
            graded = 0
            while graded < 1:
                if cam_index is not None:
                    while True:
                        raw_frame = process.stdout.read(640 * 480 * 3)
                        if not raw_frame:
                            pass
                        frame = np.frombuffer(raw_frame, np.uint8).reshape((480, 640, 3))
                        img=frame.copy()
                        break

                elif file_path is not None:

                    img = omr.omr.loadImageFromFile(self, file_path)

                cv2.imwrite("debugging-opencv/camera-test.png", img)

                img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

                index, answers, group, page_img, images_warped, page_img_grid = omr.omr.processOneSheet(self, img)
                print("finished one page")

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
                                return None
                                            
                        # save the read data to files
                        
                        # create the folder to store the data
                        if not os.path.exists("exams-data/" + currentExamName + folders[type] + str(folders_2[type])):
                            os.makedirs("exams-data/" + currentExamName + folders[type] + str(folders_2[type]))
                            
                        print("\nZczytane dpowiedzi:", answers)
                        graded += 1

                        # save the answers 
                        with open("exams-data/" + currentExamName + folders[type] + str(folders_2[type]) + "/answers.csv", "w") as f:
                            if type == 0:
                                f.write(";".join(answers))
                            if type == 1:
                                f.write(str(index) + ";" + str(answers) + ";" + str(group))

                        cv2.imwrite("exams-data/" + currentExamName + folders[type] + str(folders_2[type]) + "/page_img_" + str(graded) + ".png", page_img)
                        for im in range(len(images_warped)):
                            cv2.imwrite("exams-data/" + currentExamName + folders[type] + str(folders_2[type]) + "/answers_grid_" + str(im) + ".png", images_warped[im])

                        # won't work - different size of images
                        # cv2.imwrite(
                        #     "exams-data/" + currentExamName + folders[type] + str(folders_2[type]) + "/answers_grid_all" + str(
                        #         graded) + ".png", cv2.hconcat(images_warped))
                        transparent_img = np.ones((690, 490), dtype=np.uint8)
                        i = 0
                        for i in range(20):
                            txt = answers[i] + ", " + answers[i + 20] + ", " + answers[i + 40]
                            transparent_img = cv2.putText(transparent_img, txt, ((i+1)*20, 20), cv2.FONT_HERSHEY_SIMPLEX,
                                                1, (0,0,255,255), 2, cv2.LINE_AA)
                            i += 1

                        # grade if in student answers reading mode
                        if type == 1:
                            ans_list = ans[0].split(";")
                            print(ans_list)
                            print(answers)
                            num_questions = 55
                            score = omr.omr.score(self, ans_list[:num_questions], answers[:num_questions])
                            print("Wynik: " + str(round(score[1], 2)) + "%")
                            cv2.imwrite("exams-data/" + currentExamName + "/student_answers/" + str(index) + "/result_img.png", transparent_img)
                            score_string = str(round(score[1], 2)) + "%"
                        else:
                            score_string = ""
                        # if index is not None:
                        #     self.answerUpdateImage(page_img_grid)
                        # else:
                        #     self.answerUpdateImage(frame)



            testing = False # delete when you want to loop

        print("Finished scanning")
        if cam_index is not None:
            process.terminate()  # Zakończ proces FFmpeg
            cv2.destroyAllWindows()

        print(score_string)
        if index is not None:
            return page_img_grid, score_string, answers, group, index
        else:
            return img, None, None, None, None