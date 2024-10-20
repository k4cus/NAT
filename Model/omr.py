import base64

import cv2
import numpy as np
import statistics

from Model import utils

webcam_feed = False
path_to_image = "../data/answer_sheets/answer_sheet_5_3.png"

#cap = cv2.VideoCapture(0) # TODO delete - makes it impossible to change settings
#cap.set(10, 160)

heightImg = 3508
widthImg = 2480

heightImg = int(heightImg)
widthImg = int(widthImg)

rows = 20
columns = 5
num_answer_fields = 3

ans_array = ["A", "B", "C", "D", "E"]

#points_to_check = [[15,11], [15,489], [685,11], [693,489], [15,22], [25,11]]
points_to_check = [[10, 10], [10, 484], [681, 11], [681, 484], [10, 20], [18, 10]]
white_thresh = 120

class omr:
    controller = None

    def __init__(self, mainController):
        self.controller = mainController

    def processOneSheet(self, img):
        #img = cv2.resize(img, (widthImg, heightImg))
        imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        imgBlur = cv2.GaussianBlur(imgGray, (5, 5), 1)  # ADD GAUSSIAN BLUR
        imgCanny = cv2.Canny(imgBlur, 10, 70)  # APPLY CANNY

        # FIND ALL COUNTOURS
        imgContours = img.copy()  # COPY IMAGE FOR DISPLAY PURPOSES
        imgBigContour = img.copy()  # COPY IMAGE FOR DISPLAY PURPOSES
        contours, hierarchy = cv2.findContours(imgCanny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)  # FIND ALL CONTOURS
        rectCon = utils.rectContour(contours)  # FILTER FOR RECTANGLE CONTOURS
        biggestPoints = utils.getCornerPoints(rectCon[0])  # GET CORNER POINTS OF THE BIGGEST RECTANGLE
        biggestPoints = utils.reorder(biggestPoints)  # REORDER FOR WARPING
        thickness = 20
        cv2.drawContours(imgBigContour, biggestPoints, -1, (0, 255, 0), thickness)  # DRAW THE BIGGEST CONTOUR
        pts1 = np.float32(biggestPoints)  # PREPARE POINTS FOR WARP
        pts2 = np.float32([[0, 0], [widthImg, 0], [0, heightImg], [widthImg, heightImg]])  # PREPARE POINTS FOR WARP
        matrix = cv2.getPerspectiveTransform(pts1, pts2)  # GET TRANSFORMATION MATRIX
        imgWarpColored = cv2.warpPerspective(imgCanny, matrix, (widthImg, heightImg))  # APPLY WARP PERSPECTIVE

        # Crop image to remove the biggest contour
        margin = thickness
        imgCropped = imgWarpColored[margin:-margin, margin:-margin]
        imgContours = imgWarpColored.copy()

        self.controller.keyUpdateImage(imgCropped)
        # cv2.imshow("contour", imgCropped)
        # cv2.waitKey(5000)

        # index, answers, group_answers, page_img, images_warped = omr_read_correct_answers(img)
        # return index, answers, group_answers, page_img, images_warped


    def loadImageFromFile(self, path):
        img = cv2.imread(path)
        return img


    def load_image(self, path, webcam_feed):
        if webcam_feed:
            success, img = cap.read()
        else:
            img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
        return img


    def remove_shadows(self, img):
        rgb_planes = cv2.split(img)

        result_planes = []
        result_norm_planes = []
        for plane in rgb_planes:
            dilated_img = cv2.dilate(plane, np.ones((7, 7), np.uint8))
            bg_img = cv2.medianBlur(dilated_img, 21)
            diff_img = 255 - cv2.absdiff(plane, bg_img)
            norm_img = cv2.normalize(diff_img, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8UC1)
            result_planes.append(diff_img)
            result_norm_planes.append(norm_img)

        result = cv2.merge(result_planes)
        result_norm = cv2.merge(result_norm_planes)
        return result_norm


    def preprocess_image(self, img):
        #img = cv2.GaussianBlur(img, (3, 3), 0)
        normalized_img = np.zeros((800, 800))
        img = cv2.normalize(img, normalized_img, 0, 255, cv2.NORM_MINMAX)
        img_blur = cv2.GaussianBlur(img, (3, 3), 1)
        return img_blur


    def find_page(self, img):
        image_warped = None
        wrong_format = False
        points_to_check = [[10, 10], [10, 484], [681, 11], [681, 484], [10, 20], [18, 10]]
        img_copy = img
        # finds biggest contour in image
        contour = utils.find_contours(img, 3)
        print(len(contour))
        for cnt in contour:
            # transform
            if contour != [] and cv2.contourArea(cnt) > 90000:
                image_warped = utils.image_warping(cnt, img, 500, 700)
            else:
                print("No contour found")
                return None

            wrong_format = False
            # check if the found contour is the answer sheet and if the orientation is correct
            i = -1
            for point in points_to_check:
                i += 1
                #print(image_warped[point[0], point[1]])
                if image_warped[point[0], point[1]] < white_thresh:
                    print("Correct format")
                    continue
                else:
                    wrong_format = True
                    if i == 4 or i == 5:
                        print("Wrong orientation")
                        break
                    print("Not an answer sheet. Quitting", point)
                    break

            if wrong_format:
                continue
            if not wrong_format:
                break

        if wrong_format:
            print("Wrong format")
            return None

        if image_warped is not None:
            return image_warped[5:-5, 5:-5]
        else:
            return None


    def draw_grids(self, img, warped_imgs):
        contours = utils.find_contours2(img, num_answer_fields + 1)
        for warped_img in warped_imgs:
            back = img
            overlay = warped_img
            h, w = back.shape[:2]
            print(h, w)
            h1, w1 = overlay.shape[:2]
            print(h1, w1)
            # let store center coordinate as cx,cy
            cx, cy = (h - h1) // 2, (w - w1) // 2
            # use numpy indexing to place the resized image in the center of
            # background image

            back[cy:cy + h1, cx:cx + w1] = overlay

            # view result
        return img


    def apply_threshold(self, img):
        img_thresh = cv2.threshold(img, 170, 255, cv2.THRESH_BINARY_INV)[1]

        return img_thresh


    def draw_grid(self, img, is_index):
        if not is_index:
            return utils.drawGrid(img)
        else:
            return utils.drawGrid(img, questions=8, choices=11)


    def get_answers(self, img, img_answers_data, is_index=False):
        # search for all grid areas, find the most colored ones, add threshold
        height_answer = img_answers_data[1]
        width_answer = img_answers_data[0]
        answers_array = []

        if not is_index:
            start_height = 0
            for row in range(rows):
                answers_array_row = []
                start_width = 0
                for col in range(columns):
                    crop_img = img[start_height:start_height + height_answer, start_width:start_width + width_answer]
                    start_width += width_answer

                    average_color = crop_img.mean(axis=0).mean(axis=0)

                    answers_array_row.append(average_color)
                answers_array.append(answers_array_row)
                start_height += height_answer
            # print(answers_array)

            return answers_array

        else:
            start_width = 0
            for col in range(8):
                #print(col)
                answers_array_column = []
                start_height = 0
                for row in range(11):
                    crop_img = img[start_height:start_height + height_answer, start_width:start_width + width_answer]
                    #cv2.imshow("label", crop_img)
                    start_height += height_answer

                    average_color = crop_img.mean(axis=0).mean(axis=0)
                    answers_array_column.append(average_color)

                answers_array.append(answers_array_column)
                start_width += width_answer

            return answers_array


    def omr_read_correct_answers(self, img):
        #print("Reading correct answers from image")
        # function reads correct answers from an answer sheet
        skip_shadows = False
        img_preprocessed = self.preprocess_image(img)
        cv2.imwrite("debugging-opencv/camera-preprocessed.png", img_preprocessed)
        img = img_preprocessed
        img = self.find_page(img_preprocessed)
        page_img = img
        cv2.imwrite("debugging-opencv/found-page-1.png", img)
        if img is None:
            skip_shadows = True
            img = self.remove_shadows(img_preprocessed)
            cv2.imwrite("debugging-opencv/no-shadows-1.png", img)
            img_preprocessed = self.find_page(img)
            cv2.imwrite("debugging-opencv/found-page-2.png", img_preprocessed)
            page_img = img_preprocessed
            if img_preprocessed is None:
                return None, None, None, None, None
        #cv2.imshow("label", img)
        if not skip_shadows:
            img_preprocessed = self.remove_shadows(img)
            cv2.imwrite("debugging-opencv/no-shadows-2.png", img_preprocessed)

        img_contours = utils.find_contours(img_preprocessed, num_answer_fields + 1)
        img_contours = utils.find_contours2(img_preprocessed, num_answer_fields + 1)

        if len(img_contours) < num_answer_fields + 1:
            return None, None, None, None, None
        '''
        #make sure that the index contour is last
        for j in range(num_answer_fields + 1):
            i = j
            i2 = (j + 1) % (num_answer_fields + 1)
            #print(i, i2)
            if img_contours[i][0][0][1] > img_contours[i2][0][0][1]:
                img_contours[i],img_contours[i2] = img_contours[i2],img_contours[i]
    
        if img_contours[0][0][0][0] > img_contours[1][0][0][0]:
            img_contours[0],img_contours[1] = img_contours[1],img_contours[0]
        '''

        images_warped = []
        for contour in img_contours:
            images_warped.append(utils.image_warping(contour, img_preprocessed, widthImg, heightImg))

        im_i = 0
        for im in images_warped:
            cv2.imwrite("debugging-opencv/warped" + str(im_i) + ".png", im)
            if im_i != 3:
                im_grid = utils.drawGrid(im)
                cv2.imwrite("debugging-opencv/warped_grid" + str(im_i) + ".png", im_grid[0])
            else:
                im_grid = utils.drawGrid(im, questions=8, choices=11)
                cv2.imwrite("debugging-opencv/warped_grid" + str(im_i) + ".png", im_grid[0])
            im_i += 1

        images_threshold = []
        for warped_image in images_warped:
            #print("contour", contour)
            images_threshold.append(self.apply_threshold(warped_image))

        images_grid = []
        i = 0
        for threshold_image in images_threshold:
            if i % (num_answer_fields + 1) == num_answer_fields:
                images_grid.append(self.draw_grid(threshold_image, is_index=True))
                i = 0
            else:
                images_grid.append(self.draw_grid(threshold_image, is_index=False))  # TODO delete unnecessary data
                i += 1
        #cv2.imshow("label3", images_grid[2][0])
        images_answers = []
        i = 0
        for grid in images_grid:
            if i % (num_answer_fields + 1) == num_answer_fields:
                images_answers.append(self.get_answers(grid[0], grid[1], is_index=True))
                i = 0
            else:
                images_answers.append(self.get_answers(grid[0], grid[1]))
                i += 1

        # grade answers
        all_answers = []
        for answer in images_answers[:-1]:
            answers = []
            for question in answer:
                #print(max(question))
                if max(question) * 0.50 > statistics.median(question):
                    answers.append(ans_array[question.index(max(question))])
                else:
                    answers.append("0")
            all_answers.append(answers)
        full_answers = []
        for l in all_answers:
            for a in l:
                full_answers.append(a)
        #print(full_answers)

        # read the index
        index_answer = images_answers[-1][:-2]
        #print(index_answer)
        index_answers = []
        for char in index_answer:
            index_answers.append(str(char.index(max(char)) - 1))
        index_txt = "".join(index_answers)

        group_answer = images_answers[-1][-1]
        group = group_answer.index(max(group_answer))
        #print("Grupa:",group)
        warped_imgs_grid = [1]
        #page_img_grid = draw_grids(page_img, images_warped)
        #print(index_txt, full_answers, group, page_img, warped_imgs_grid)
        #cv2.imshow("label", page_img)
        return index_txt, full_answers, group, page_img, images_warped


    def omr_grade(self, correct_answers, img):
        #print("Reading student's answers from image")
        # function grades answers based on the correct answers in the argument
        skip_shadows = False
        img_preprocessed = self.preprocess_image(img)
        cv2.imwrite("debugging-opencv/camera-preprocessed.png", img_preprocessed)
        img = self.find_page(img_preprocessed)
        page_img = img
        if img is not None:
            cv2.imwrite("debugging-opencv/found-page-1.png", img)
        if img is None:
            skip_shadows = True
            img = self.remove_shadows(img_preprocessed)
            cv2.imwrite("debugging-opencv/no-shadows-1.png", img)
            img_preprocessed = self.find_page(img)
            page_img = img_preprocessed
            if img_preprocessed is not None:
                cv2.imwrite("debugging-opencv/found-page-2.png", img_preprocessed)
            if img_preprocessed is None:
                return None, None, None, None, None
        #cv2.imshow("label", img)
        if not skip_shadows:
            img_preprocessed = self.remove_shadows(img)
            cv2.imwrite("debugging-opencv/no-shadows-2.png", img_preprocessed)

        img_contours = utils.find_contours(img_preprocessed, num_answer_fields + 1)
        img_contours = utils.find_contours2(img_preprocessed, num_answer_fields + 1)
        print("cnt found")
        if len(img_contours) < 3:
            return None, None, None, None, None

        '''
        #make sure that the index contour is last
        for j in range(num_answer_fields + 1):
            i = j
            i2 = (j + 1) % (num_answer_fields + 1)
            #print(i, i2)
            if img_contours[i][0][0][1] > img_contours[i2][0][0][1]:
                img_contours[i],img_contours[i2] = img_contours[i2],img_contours[i]
        '''

        if img_contours[0][0][0][0] > img_contours[1][0][0][0]:
            img_contours[0], img_contours[1] = img_contours[1], img_contours[0]

        images_warped = []
        for contour in img_contours:
            images_warped.append(utils.image_warping(contour, img_preprocessed, widthImg, heightImg))

        im_i = 0
        for im in images_warped:
            cv2.imwrite("debugging-opencv/warped" + str(im_i) + ".png", im)
            if im_i != 3:
                im_grid = utils.drawGrid(im)
                cv2.imwrite("debugging-opencv/warped_grid" + str(im_i) + ".png", im_grid[0])
            else:
                im_grid = utils.drawGrid(im, questions=8, choices=11)
                cv2.imwrite("debugging-opencv/warped_grid" + str(im_i) + ".png", im_grid[0])
            im_i += 1

        images_threshold = []
        for warped_image in images_warped:
            images_threshold.append(self.apply_threshold(warped_image))

        images_grid = []
        i = 0
        for threshold_image in images_threshold:
            if i % (num_answer_fields + 1) == num_answer_fields:
                images_grid.append(self.draw_grid(threshold_image, is_index=True))
                i = 0
            else:
                images_grid.append(self.draw_grid(threshold_image, is_index=False))  # TODO delete unnecessary data
                i += 1

        images_answers = []
        i = 0
        for grid in images_grid:
            if i % (num_answer_fields + 1) == num_answer_fields:
                images_answers.append(self.get_answers(grid[0], grid[1], is_index=True))
                i = 0
            else:
                images_answers.append(self.get_answers(grid[0], grid[1]))
                i += 1

        # grade answers
        all_answers = []
        for answer in images_answers[:-1]:
            answers = []
            for question in answer:
                #print(max(question))
                if max(question) * 0.50 > statistics.median(question):
                    answers.append(ans_array[question.index(max(question))])
                else:
                    answers.append("0")
            all_answers.append(answers)
        full_answers = []
        for l in all_answers:
            for a in l:
                full_answers.append(a)
        #print("\nOdpowiedzi:         ", full_answers)

        # read the index
        index_answer = images_answers[-1][:-2]
        index_answers = []
        for char in index_answer:
            index_answers.append(str(char.index(max(char)) - 1))
        index_txt = "".join(index_answers)

        group_answer = images_answers[-1][-1]
        group = group_answer.index(max(group_answer))
        #print("Grupa:",group)
        warped_imgs_grid = []
        return index_txt, full_answers, group, page_img, images_warped

    def imageToBase64(self, img):
        _, buffer = cv2.imencode('.png', img)
        return base64.b64encode(buffer).decode('utf-8')

    def score(self, correct, answers):
        return utils.score(correct, answers)

#
# if __name__ == '__main__':
#     graded = False
#     type = 1 # TODO loadning correct answers
#     while graded == False:
#         if type == 0:
#             _, answers, group_answers = omr_read_correct_answers()
#             print("\nPoprawne odpowiedzi:", answers)
#             if answers is not None:
#                 graded = True
#         if type == 1:
#             _, answers, group_answers = omr_read_correct_answers()
#             print("\nPoprawne odpowiedzi:", answers)
#
#             index, score, group = omr_grade(answers, path_to_image)
#             if index is not None:
#                 print("\nIndeks:", index, "\nWynik:", score, "\nGrupa:", group)
#             if answers is not None and score is not None:
#                 graded = True
#
#     data = usos_utils.import_data()
#     export_csv = usos_utils.export_data({index: score}, data, score)
#     print(export_csv)
#
