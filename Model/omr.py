import base64

import cv2
import numpy as np
import statistics

from Model import utils

heightImg = 3508
widthImg = 2480

heightImg = int(heightImg)
widthImg = int(widthImg)

rows = 20
columns = 5
num_answer_fields = 3

ans_array = ["A", "B", "C", "D", "E"]

points_to_check = [[10, 10], [10, 484], [681, 11], [681, 484], [10, 20], [18, 10]]
white_thresh = 120

class omr:
    controller = None

    def __init__(self, mainController):
        self.controller = mainController

    def processOneSheet(self, img):
        # function reads correct answers from an answer sheet
        skip_shadows = False   	

        img_preprocessed = omr.preprocess_image(self, img)
        cv2.imwrite("debugging-opencv/camera-preprocessed.png", img_preprocessed)
        img = img_preprocessed
        img = omr.find_page(self, img_preprocessed)
        page_img = img

        try:
            cv2.imwrite("debugging-opencv/found-page-1.png", img)
        except:
            print("No page found")

        if img is None:
            skip_shadows = True
            img = omr.remove_shadows(self, img_preprocessed)
            cv2.imwrite("debugging-opencv/no-shadows-1.png", img)
            img_preprocessed = omr.find_page(self, img)

            try:
                cv2.imwrite("debugging-opencv/found-page-2.png", img_preprocessed)
            except:
                print("No page found")
            
            page_img = img_preprocessed
            if img_preprocessed is None:
                return None, None, None, None, None
            
        if not skip_shadows:
            img_preprocessed = omr.remove_shadows(self, img)

        img_contours = utils.find_contours(img_preprocessed, num_answer_fields + 1)
        img_contours = utils.find_contours2(img_preprocessed, num_answer_fields + 1)

        if len(img_contours) < num_answer_fields + 1:
            return None, None, None, None, None

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
            images_threshold.append(omr.apply_threshold(self, warped_image))

        images_grid = []
        i = 0
        for threshold_image in images_threshold:
            if i % (num_answer_fields + 1) == num_answer_fields:
                images_grid.append(omr.draw_grid(self, threshold_image, is_index=True))
                i = 0
            else:
                images_grid.append(omr.draw_grid(self, threshold_image, is_index=False))  # TODO delete unnecessary data
                i += 1

        images_answers = []
        i = 0
        for grid in images_grid:
            if i % (num_answer_fields + 1) == num_answer_fields:
                images_answers.append(omr.get_answers(self, grid[0], grid[1], is_index=True))
                i = 0
            else:
                images_answers.append(omr.get_answers(self, grid[0], grid[1]))
                i += 1

        # grade answers
        all_answers = []
        for answer in images_answers[:-1]:
            answers = []
            for question in answer:
                if max(question) * 0.50 > statistics.median(question):
                    answers.append(ans_array[question.index(max(question))])
                else:
                    answers.append("0")
            all_answers.append(answers)
        full_answers = []
        for l in all_answers:
            for a in l:
                full_answers.append(a)

        # read the index
        index_answer = images_answers[-1][:-2]

        index_answers = []
        for char in index_answer:
            index_answers.append(str(char.index(max(char)) - 1))
        index_txt = "".join(index_answers)

        group_answer = images_answers[-1][-1]
        group = group_answer.index(max(group_answer))

        warped_imgs_grid = [1]
        print(index_txt, full_answers, group, page_img, warped_imgs_grid)
        page_img_grid = omr.draw_grids(self, page_img, images_warped, [index_txt, group], full_answers)
        
        cv2.imwrite("debugging-opencv/grid_full_answers.png", page_img_grid)

        return index_txt, full_answers, group, page_img, images_warped, page_img_grid



    def loadImageFromFile(self, path):
        img = cv2.imread(path)
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
            '''
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
        '''
        if image_warped is not None:
            return image_warped[5:-5, 5:-5]
        else:
            return None


    def draw_grids(self, img, warped_imgs, index_group, full_answers):
        contours = utils.find_contours3(img, num_answer_fields + 1)
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
        img = cv2.applyColorMap(img, cv2.COLORMAP_PINK)
        #img2 = cv2.drawContours(img, contours, -1, (255, 255, 0), 2)
        i = 0
        for contour in contours[:-1]:
            img = utils.drawGridFullPage(img, contour, index_group, full_answers, i)
            i += 1
        img = utils.drawGridFullPage(img, contours[-1], index_group, full_answers, i, questions=8, choices=11)
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

    def imageToBase64(self, img):
        _, buffer = cv2.imencode('.png', img)
        return base64.b64encode(buffer).decode('utf-8')

    def score(self, correct, answers):
        return utils.score(correct, answers)

def score(correct, answers):
    points = 0
    num_of_questions = len(correct)
    for question in range(num_of_questions):
        if correct[question] == answers[question]:
            points += 1
    score = 100 * points / num_of_questions
    return points, score