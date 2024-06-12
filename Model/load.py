import cv2
import sys
import os
sys.path.append("..")
from OMR import OMR_main as omr
import numpy as np

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

    def loadAnswers(self, type, currentExamName, cam_index):
        #path_to_image = "data/answer_sheets/answer_sheet_5_8.jpg"
        #img = omr.load_image(path_to_image, False)

        cap = cv2.VideoCapture(cam_index)
        cap.set(10, 160)

        testing = True
        while testing:
            graded = 0
            while graded < 1:
                success, img = cap.read()
                cv2.imwrite("debugging-opencv/camera-test.png", img)
                img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

                if type == 0:  # Only scan correct answers
                    _, answers, group_answers, page_img, images_warped = omr.omr_read_correct_answers(img)

                    if answers is not None:
                        if not os.path.exists("exams-data/" + currentExamName + "/answer_keys/" + str(group_answers)):
                            os.makedirs("exams-data/" + currentExamName + "/answer_keys/" + str(group_answers))
                        print("Poprawne odpowiedzi:", answers)
                        graded += 1
                        with open("exams-data/" + currentExamName + "/answer_keys/" + str(group_answers) + "/answers.csv", "w") as f:
                            f.write(";".join(answers))

                        cv2.imwrite("exams-data/" + currentExamName + "/answer_keys/" + str(group_answers) + "/page_img_" + str(graded) + ".png", page_img)
                        for im in range(len(images_warped)):
                            cv2.imwrite("exams-data/" + currentExamName + "/answer_keys/" + str(group_answers) + "/answers_grid_" + str(im) + ".png", images_warped[im])
                        cv2.imwrite(
                            "exams-data/" + currentExamName + "/answer_keys/" + str(group_answers) + "/answers_grid_all" + str(
                                graded) + ".png", cv2.hconcat(images_warped))
                        transparent_img = np.ones((690, 490), dtype=np.uint8)
                        i = 0
                        for i in range(20):
                            txt = answers[i] + ", " + answers[i + 20] + ", " + answers[i + 40]
                            transparent_img = cv2.putText(transparent_img, txt, ((i+1)*20, 20), cv2.FONT_HERSHEY_SIMPLEX,
                                                1, (0,0,255,255), 2, cv2.LINE_AA)
                            i += 1
                        cv2.imwrite("exams-data/" + currentExamName + "/answer_keys/result_img.png", transparent_img)

                if type == 1:  # scan student's answers
                    answers1 = []
                    index, answers, group, page_img, images_warped = omr.omr_grade(answers1, img)

                    if index is not None:
                        print("\nIndeks:", index, "\nWynik:", answers, "\nGrupa:", group)

                    if answers is not None and answers is not None:
                        if not os.path.exists("exams-data/" + currentExamName + "/answer_keys/" + str(group)):
                            os.makedirs("exams-data/" + currentExamName + "/answer_keys/" + str(group))
                        with open("exams-data/" + currentExamName + "/answer_keys/" + str(group) + "/answers.csv", "a+") as f:
                            f.seek(0)
                            ans = f.readlines()
                        if ans == []:
                            print("No answers to load. First scan the answer sheet or create the csv file manually.")
                        graded += 1
                        if not os.path.exists("exams-data/" + currentExamName + "/student_answers/" + str(index)):
                            os.makedirs("exams-data/" + currentExamName + "/student_answers/" + str(index))
                        with open("exams-data/" + currentExamName + "/student_answers/" + str(index) + "/answers.csv", "w") as f:
                            f.write(str(index) + ";" + str(answers) + ";" + str(group))
                        cv2.imwrite("exams-data/" + currentExamName + "/student_answers/" + str(index) + "/page_img_" + str(graded) + ".png", page_img)
                        for im in range(len(images_warped)):
                            cv2.imwrite("exams-data/" + currentExamName + "/student_answers/" + str(index) + "/answers_grid_" + str(im) + ".png", images_warped[im])
                        cv2.imwrite(
                            "exams-data/" + currentExamName + "/student_answers/" + str(index) + "/answers_grid_all" + str(
                                graded) + ".png", cv2.hconcat(images_warped))
                        transparent_img = np.zeros((690, 490, 4), dtype=np.uint8)
                        i = 0
                        for i in range(20):
                            txt = answers[i] + ", " + answers[i + 20] + ", " + answers[i + 40]
                            transparent_img = cv2.putText(transparent_img, txt, (20, (i+1)*30), cv2.FONT_HERSHEY_SIMPLEX,
                                                1, (0,0,255,255), 2, cv2.LINE_AA)
                            i += 1

                        ans_list = ans[0].split(";")
                        print(ans_list)
                        print(answers)
                        num_questions = 55
                        score = omr.score(ans_list[:num_questions], answers[:num_questions])
                        print("Wynik: " + str(round(score[1], 2)) + "%")
                        cv2.imwrite("exams-data/" + currentExamName + "/student_answers/" + str(index) + "/result_img.png", transparent_img)

            testing = False # delete when you want to loop
        cv2.imwrite("assets/page.png", page_img)  # saves the last scanned image to display it later - not working
        print("Finished scanning")
        cap.release()


        return None

    def loadAnswersFromFolder(self, type, currentExamName, path):
        num_questions = 55
        ind = 0
        not_read = 0
        files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
        #print(files)
        for file in files:
            imfile = os.path.join(path, file)
            print(imfile)
            img = omr.load_image(imfile, False)

            testing = True
            while testing:
                graded = 0
                while graded < 1:
                    graded += 1
                    #img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

                    if type == 0:  # Only scan correct answers
                        index, answers, group_answers, page_img, images_warped = omr.omr_read_correct_answers(img)

                        if answers is not None:
                            if not os.path.exists("exams-data/" + currentExamName + "/answer_keys/" + str(group_answers)):
                                os.makedirs("exams-data/" + currentExamName + "/answer_keys/" + str(group_answers))
                            if not os.path.exists("exams-data/" + currentExamName + "/answer_keys/all_graded"):
                                os.makedirs("exams-data/" + currentExamName + "/answer_keys/all_graded")
                            #print("\nGrupa:", group_answers)
                            #print("\nPoprawne odpowiedzi:", answers)
                            graded += 1
                            with open("exams-data/" + currentExamName + "/answer_keys/" + str(group_answers) + "/answers.csv", "w") as f:
                                f.write(";".join(answers))

                            cv2.imwrite("exams-data/" + currentExamName + "/answer_keys/" + str(group_answers) + "/page_img_" + str(graded) + ".png", page_img)
                            for im in range(len(images_warped)):
                                cv2.imwrite("exams-data/" + currentExamName + "/answer_keys/" + str(group_answers) + "/answers_grid_" + str(im) + ".png", images_warped[im])
                            cv2.imwrite(
                                "exams-data/" + currentExamName + "/answer_keys/" + str(group_answers) + "/answers_grid_all" + str(
                                    graded) + ".png", cv2.hconcat(images_warped))
                            transparent_img = np.ones((690, 490), dtype=np.uint8)
                            i = 0
                            for i in range(20):
                                txt = answers[i] + ", " + answers[i + 20] + ", " + answers[i + 40]
                                transparent_img = cv2.putText(transparent_img, txt, ((i+1)*20, 20), cv2.FONT_HERSHEY_SIMPLEX,
                                                    1, (0,0,255,255), 2, cv2.LINE_AA)
                                i += 1
                            #cv2.imwrite("exams-data/" + currentExamName + "/answer_keys/result_img.png", transparent_img)
                            img_circles = omr.draw_grids(page_img, answers, index=None, group=group_answers)
                            cv2.imwrite(
                            "exams-data/" + currentExamName + "/answer_keys/" + str(
                                group_answers) + "/image_shown_answers_" + str(
                                graded) + ".png", img_circles)
                            cv2.imwrite(
                            "exams-data/" + currentExamName + "/answer_keys/all_graded/image_shown_answers_" + str(
                                group_answers) + ".png", img_circles)
                            with open("exams-data/" + currentExamName + "/answer_keys/all_graded/image_shown_answers_" + str(
                                group_answers) + ".txt", "w+") as f:
                                for a in range(len(answers[:num_questions])):
                                    f.write(str(a+1) + ". " + str(answers[a]) + "\n")
                        else:
                            img = cv2.imread(imfile)
                            if not os.path.exists("exams-data/" + currentExamName + "/student_answers/not_read/"):
                                os.makedirs("exams-data/" + currentExamName + "/student_answers/not_read/")
                            cv2.imwrite("exams-data/" + currentExamName + "/student_answers/not_read/" + str(not_read) + ".png", img)
                            not_read += 1


                    if type == 1:  # scan student's answers
                        answers1 = []
                        index, answers, group, page_img, images_warped = omr.omr_grade(answers1, img)

                        if index is not None:
                            print("\nIndeks:", index, "\nWynik:", answers, "\nGrupa:", group)
                            if len(index)!=6:
                                index = "9999" + str(ind).zfill(2)
                                ind += 1
                        if answers is not None:
                            if not os.path.exists("exams-data/" + currentExamName + "/answer_keys/" + str(group)):
                                os.makedirs("exams-data/" + currentExamName + "/answer_keys/" + str(group))
                            if not os.path.exists("exams-data/" + currentExamName + "/student_answers/all_graded"):
                                os.makedirs("exams-data/" + currentExamName + "/student_answers/all_graded")
                            with open("exams-data/" + currentExamName + "/answer_keys/" + str(group) + "/answers.csv", "a+") as f:
                                f.seek(0)
                                ans = f.readlines()
                            if ans == []:
                                print("No answers to load. First scan the answer sheet or create the csv file manually.")

                            graded += 1
                            if not os.path.exists("exams-data/" + currentExamName + "/student_answers/" + str(index)):
                                os.makedirs("exams-data/" + currentExamName + "/student_answers/" + str(index))
                            with open("exams-data/" + currentExamName + "/student_answers/" + str(index) + "/answers.csv", "w") as f:
                                f.write(str(index) + ";" + str(answers) + ";" + str(group))
                            cv2.imwrite("exams-data/" + currentExamName + "/student_answers/" + str(index) + "/page_img_" + str(graded) + ".png", page_img)
                            for im in range(len(images_warped)):
                                cv2.imwrite("exams-data/" + currentExamName + "/student_answers/" + str(index) + "/answers_grid_" + str(im) + ".png", images_warped[im])
                            cv2.imwrite(
                                "exams-data/" + currentExamName + "/student_answers/" + str(index) + "/answers_grid_all" + str(
                                    graded) + ".png", cv2.hconcat(images_warped))
                            transparent_img = np.zeros((690, 490, 4), dtype=np.uint8)
                            i = 0
                            for i in range(20):
                                txt = answers[i] + ", " + answers[i + 20] + ", " + answers[i + 40]
                                transparent_img = cv2.putText(transparent_img, txt, (20, (i+1)*30), cv2.FONT_HERSHEY_SIMPLEX,
                                                    1, (0,0,255,255), 2, cv2.LINE_AA)
                                i += 1
                            if ans != []:
                                ans_list = ans[0].split(";")
                                #print(ans_list)
                                #print(answers)
                                score = omr.score(ans_list[:num_questions], answers[:num_questions])
                                #print("Wynik: " + str(round(score[1], 2)) + "%")
                            #cv2.imwrite("exams-data/" + currentExamName + "/student_answers/" + str(index) + "/result_img.png", transparent_img)
                            img_circles = omr.draw_grids(page_img, answers, index, group=group)
                            cv2.imwrite(
                            "exams-data/" + currentExamName + "/student_answers/" + str(
                                index) + "/image_shown_answers_" + str(
                                graded) + ".png", img_circles)
                            cv2.imwrite(
                            "exams-data/" + currentExamName + "/student_answers/all_graded/image_shown_answers_" + str(
                                index) + ".png", img_circles)
                            with open("exams-data/" + currentExamName + "/student_answers/all_graded/image_shown_answers_" + str(
                                index) + ".txt", "w+") as f:
                                f.write(str(index) + "\n")
                                f.write(str(group) + "\n")
                                for a in range(len(answers[:num_questions])):
                                    f.write(str(a+1) + ". " + str(answers[a]) + "\n")
                        else:
                            img = cv2.imread(imfile)
                            if not os.path.exists("exams-data/" + currentExamName + "/student_answers/not_read/"):
                                os.makedirs("exams-data/" + currentExamName + "/student_answers/not_read/")
                            cv2.imwrite("exams-data/" + currentExamName + "/student_answers/not_read/file_" + str(not_read) + ".png", img)
                            not_read += 1
                testing = False # delete when you want to loop
        return None

    def saveToCSV(self, currentExamName):
        grades = {
            0: 2,
            1: 2,
            2: 2,
            3: 2,
            4: 2,
            5: 3,
            6: 3.5,
            7: 4,
            8: 4.5,
            9: 5,
            10: 5
        }
        csv_rows = []
        csv_rows.append("indeks;punkty;ocena;\n")
        path = "exams-data/" + currentExamName + "/student_answers/all_graded/"
        for filename in os.listdir(path):
            if filename.endswith('.txt'):
                print("student:",os.path.join(path, filename))
                with open(os.path.join(path, filename)) as f:
                    file_contents = f.readlines()
                index = file_contents[0].strip()
                group = file_contents[1].strip()
                answers = []
                for answer in file_contents[2:]:
                    #print(answer)
                    answers.append(answer.split()[1].strip())
                print("exams-data/" + currentExamName + "/answer_keys/" + str(group) + "/answers.csv")
                with open("exams-data/" + currentExamName + "/answer_keys/" + str(group) + "/answers.csv", "a+") as f:
                    f.seek(0)
                    correct_answers = f.readlines()
                correct_answers_list = correct_answers[0].split(";")[:55]
                #print("poprawne:",correct_answers_list)
                #print("studenta:",answers)
                score, grade = omr.score(correct_answers_list,answers)
                print(score, grade)
                grade_txt = grades[int(grade/10)]
                print(grade_txt)
                csv_rows.append(index + ";" + str(score) + ";" + str(grade_txt) + ";\n")
            with open("exams-data/" + currentExamName + "/answers.csv", "w+") as f:
                for row in csv_rows:
                    f.write(row)
        print("Done")



