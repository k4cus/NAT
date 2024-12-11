import base64

import cv2
import numpy as np
import statistics
from PIL import ImageGrab

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


# np.set_printoptions(threshold = np.inf)

class omr:
    controller = None

    def __init__(self, mainController):
        self.controller = mainController

    def processOneSheet(self, img, cropped=False, coords=None):
        # function reads correct answers from an answer sheet
        img_preprocessed = None
        skip_shadows = False
        if cropped:
            page_img = img
        if not cropped:

            img_preprocessed = omr.preprocess_image(self, img)
            cv2.imwrite("debugging-opencv/1_camera-preprocessed.png", img_preprocessed)
            img = img_preprocessed
            img = omr.find_page(self, img_preprocessed)
            page_img = img

            try:
                cv2.imwrite("debugging-opencv/2_found-page-1.png", img)
            except:
                print("No page found")

            if img is None:
                skip_shadows = True
                img = omr.remove_shadows(self, img_preprocessed)
                cv2.imwrite("debugging-opencv/2_no-shadows-1.png", img)
                img_preprocessed = omr.find_page(self, img)

                try:
                    cv2.imwrite("debugging-opencv/2_found-page-2.png", img_preprocessed)
                except:
                    print("No page found")

                page_img = img_preprocessed
                if img_preprocessed is None:
                    return None, None, None, None, None

        if not skip_shadows:
            img_preprocessed = omr.remove_shadows(self, img)

        if coords is not None:
            screenshot = np.array(ImageGrab.grab(bbox=(None)))
            img_preprocessed = omr.find_page(self, screenshot, coords)
            page_img = img_preprocessed
            img_preprocessed = cv2.cvtColor(img_preprocessed, cv2.COLOR_BGR2GRAY)

        # hardcoded positions of tables
        imgRectangles = [
            # utils.cropRectangle([70, 625], [329, 1320]),  # table with answers 1
            # utils.cropRectangle([380, 625], [642, 1320]),  # table with answers 2
            # utils.cropRectangle([692, 625], [956, 1320]),  # table with answers 3
            # utils.cropRectangle([260, 50], [670, 454])  # table with index number

            utils.cropRectangle([37, 341], [199, 742]),
            utils.cropRectangle([224, 341], [387, 742]),  # table with answers 2
            utils.cropRectangle([413, 341], [576, 742]),  # table with answers 3
            utils.cropRectangle([158, 38], [402, 258])  # table with index number
        ]

        imgRectangles = np.array(imgRectangles)  # convert to numpy array
        # img_contours = utils.find_contours2(img_preprocessed, num_answer_fields + 1)

        if len(imgRectangles) < num_answer_fields + 1 or img_preprocessed is None:
            return None, None, None, None, None

        images_warped = []
        for i, imgRectangle in enumerate(imgRectangles):
            # cut out each table with margin around
            tableWithMargin = (utils.image_warping(np.array(imgRectangle.getContour()), img_preprocessed, imgRectangle.getWidth(),
                                                   imgRectangle.getHeight()))  # width, height
            cv2.imwrite("debugging-opencv/3a_tableWithMargin" + str(i) + ".png", tableWithMargin)
            # find contours for each table
            if i < 3:
                cnt = utils.find_contours_tables(tableWithMargin, 1)
            else:
                cnt = utils.find_contours_tables(tableWithMargin, 1, index=True)
            # imgRectangle.updateFromRelativeContour(cnt)

            # cut out each table to remove margins
            # tableWithoutMargin = (utils.image_warping(np.array(imgRectangle.getContour()), img_preprocessed, imgRectangle.getWidth(),
            #                                        imgRectangle.getHeight()))
            # tableWithoutMargin = utils.image_warping(cnt, tableWithMargin, imgRectangle.getWidth(), imgRectangle.getHeight())
            images_warped.append(cnt)


        # store to disk for debbuging
        images_threshold = []
        images_grid = []
        for im_i, im in enumerate(images_warped):
            cv2.imwrite("debugging-opencv/3_warped" + str(im_i) + ".png", im)
            images_threshold.append(omr.apply_threshold(self, im))

            if im_i != 3:
                im_grid = utils.drawGrid(im)
                cv2.imwrite("debugging-opencv/3_warped_grid" + str(im_i) + ".png", im_grid[0])
            else:
                im_grid = utils.drawGrid(im, questions=8, choices=11)
                cv2.imwrite("debugging-opencv/3_warped_grid" + str(im_i) + ".png", im_grid[0])
            im_i += 1

        i = 0
        # print("Images threshold:", images_threshold)
        for threshold_image in images_threshold:
            if i % (num_answer_fields + 1) == num_answer_fields:
                images_grid.append(utils.drawGrid(threshold_image, questions=8, choices=11))
                i = 0
            else:
                images_grid.append(utils.drawGrid(threshold_image))  # TODO delete unnecessary data
                i += 1

        images_answers = []
        i = 0
        for grid in images_grid:
            if i % (num_answer_fields + 1) == num_answer_fields:
                cv2.imwrite("debugging-opencv/5_full_img_index" + str(i) + ".png", grid[0])
                images_answers.append(omr.get_answers(self, grid[0], grid[1], is_index=True))
                i = 0
            else:
                cv2.imwrite("debugging-opencv/5_full_img" + str(i) + ".png", grid[0])
                images_answers.append(omr.get_answers(self, grid[0], grid[1]))
                i += 1

        # grade answers
        all_answers = []
        for answer in images_answers[:-1]:
            answers = []
            for question in answer:
                # question2 = question/max(question)
                print("Question:", question, statistics.median(question))
                if 2 * statistics.median(question) < max(question) and max(question) > 100:
                    # print("Question:", question2)
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
        page_img_grid = omr.draw_grids(self, page_img, imgRectangles, [index_txt, group], full_answers)

        cv2.imwrite("debugging-opencv/4_grid_full_answers.png", page_img_grid)
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
        # img = cv2.GaussianBlur(img, (3, 3), 0)
        normalized_img = np.zeros((800, 800))
        img = cv2.normalize(img, normalized_img, 0, 255, cv2.NORM_MINMAX)
        img_blur = cv2.GaussianBlur(img, (3, 3), 1)
        return img_blur

    def find_page(self, img, coords=None):
        '''
        image_warped = None
        wrong_format = False
        img_copy = img
        coords_2 = []

        # finds biggest contour in image
        if coords is None:
            contour = utils.find_contours(img, 3)
        else:
            for c in range(len(coords)):
                coords_2.append([coords[c]])

            contour1 = np.array(coords_2)
            contour = [np.array(contour1)]

        for cnt in contour:
            # transform
            # if contour != [] and cv2.contourArea(cnt) > 90000:
            if contour != []:
                image_warped = utils.image_warping(cnt, img, 1000, 1400)
                cv2.imwrite("debugging-opencv/new_img_warped.png", image_warped)
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
                    wrong_format = Trumatrixe
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
        image_warped = utils.find_contours_page(img, 3)
        if image_warped is not None:
            return image_warped[5:-5, 5:-5]
        else:
            return None

    def draw_grids(self, img, imgRectangles, index_group, full_answers):
        try:
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
        except:
            pass
        img = cv2.applyColorMap(img, cv2.COLORMAP_PINK)
        # img2 = cv2.drawContours(img, contours, -1, (255, 255, 0), 2)

        for i, imgRectangle in enumerate(imgRectangles):
            cnt = imgRectangle.getContour()
            if i == 3:
                # table with index number
                img = utils.drawGridFullPage(img, imgRectangles[-1].getContour(), index_group, full_answers, i, questions=8, choices=11)
            else:
                # tables with answers
                img = utils.drawGridFullPage(img, cnt, index_group, full_answers, i)

        #
        # view result
        return img

    def apply_threshold(self, img):
        # print("Img 0:", img)
        img_flattened = [item for sublist in img for item in sublist]
        img_median = statistics.median(img_flattened)
        print("Median:", img_median)
        cv2.imwrite("debugging-opencv/thresh_test.png", img)
        #img_thresh = cv2.threshold(img, 280 - img_median, 255, cv2.THRESH_BINARY)[1]
        img_thresh = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

        cv2.imwrite("debugging-opencv/thresh_test_2.png", img_thresh)
        # print("Img:", img_thresh)
        # print("Img 3:", img)
        return img_thresh

    def get_answers(self, img, img_answers_data, is_index=False):
        # search for all grid areas, find the most colored ones, add threshold
        # print("Img:", img)
        # print("Img answers data:", img_answers_data)

        height_answer = img_answers_data[1]
        width_answer = img_answers_data[0]
        answers_array = []

        if not is_index:
            # tables with answers
            start_height = 0
            for row in range(rows):
                answers_array_row = []
                start_width = 0

                for col in range(columns):
                    # 0 - black, 255 - white
                    crop_img = img[round(start_height):round(start_height + height_answer), round(start_width):round(start_width + width_answer)]
                    
                    crop_img_size = [crop_img.shape[0], crop_img.shape[1]]
                    mask= np.ones((crop_img_size[0], crop_img_size[1]), dtype=np.uint8) * 127
                    circle_center = (crop_img_size[1] // 2, crop_img_size[0] // 2)  # Center of the circle
                    circle_radius = 2*crop_img_size[0] // 5  # Radius of the circle
                    circle_color = 0  # Black color
                    circle_thickness = -1

                    cv2.circle(mask, circle_center, circle_radius, circle_color, circle_thickness)
                    cv2.imwrite("debugging-opencv/5_mask_img.png", mask)

                    mask_negative = np.ones((crop_img_size[0], crop_img_size[1]), dtype=np.uint8) * 0
                    circle_center = (crop_img_size[1] // 2, crop_img_size[0] // 2)  # Center of the circle
                    circle_radius = 2*crop_img_size[0] // 5  # Radius of the circle
                    circle_color = 127  # Black color
                    circle_thickness = -1

                    cv2.circle(mask_negative, circle_center, circle_radius, circle_color, circle_thickness)
                    cv2.imwrite("debugging-opencv/5_mask_img_negative.png", mask_negative)

                    #print("Size of the cropped img: ", crop_img_size)
                    cv2.imwrite("debugging-opencv/5_cropped_img.png", crop_img)
                    start_width += width_answer
                    # print("img 1:", crop_img)
                    crop_img_flattened = [item for sublist in crop_img for item in sublist]
                    # print("Img max:", max(crop_img_flattened))
                    # print("Img min:", min(crop_img_flattened))
                    # crop_img_flattened = crop_img_flattened - min(crop_img_flattened)
                    crop_img_flattened = crop_img_flattened / max(crop_img_flattened)
                    # average_color = statistics.mean(crop_img_flattened)
                    # crop_img_median = statistics.median(crop_img_flattened)

                    # print("Img 2:", crop_img_flattened)

                    #print(crop_img)
                    #print(mask)
                    matching_pixels = np.sum(crop_img == mask)
                    matching_pixels_negative = np.sum(crop_img == mask_negative)
                    print(f"Matching Pixels: ", matching_pixels, matching_pixels_negative)

                    #black_count = 0
                    #white_count = 0
                    #for pixel in crop_img_flattened:
                    #    if pixel > 0.8:
                    #        white_count += 1
                    #    else:
                    #        black_count += 1

                    # print("Black:", black_count)
                    # print("White:", white_count)
                    # print("Percent:", percent)
                    # print("Img:", crop_img_flattened)
                    # print("Median:", crop_img_median)
                    # print("Avg color:", average_color)
                    # print("Sum:", sum(crop_img_flattened))
                    if matching_pixels_negative > 500:
                        print("wrong answer")
                        matching_pixels = 0

                    answers_array_row.append(matching_pixels)
                answers_array.append(answers_array_row)
                start_height += height_answer
            # print("Answers array:", answers_array)

            # print("Answers array median:", statistics.median(flattened_list)/max(flattened_list))
            # print("Answers array max:", max(flattened_list)/max(flattened_list))
            # print("Answers array min:", min(flattened_list)/max(flattened_list))
            # print("Answers array avg:", statistics.mean(flattened_list)/max(flattened_list))

            return answers_array

        else:
            # table with index number
            start_width = 0
            for col in range(8):
                answers_array_column = []
                start_height = 0
                for row in range(11):
                    crop_img = img[round(start_height):round(start_height + height_answer), round(start_width):round(start_width + width_answer)]
                    #cv2.imwrite("debugging-opencv/6_crop_img_index" + str(row) + ".png", crop_img)
                    crop_img_size = [crop_img.shape[0], crop_img.shape[1]]

                    mask= np.ones((crop_img_size[0], crop_img_size[1]), dtype=np.uint8) * 127
                    circle_center = (crop_img_size[1] // 2, crop_img_size[0] // 2)  # Center of the circle
                    circle_radius = 2*crop_img_size[0] // 5  # Radius of the circle
                    circle_color = 0  # Black color
                    circle_thickness = -1

                    cv2.circle(mask, circle_center, circle_radius, circle_color, circle_thickness)
                    cv2.imwrite("debugging-opencv/6_mask_img_index.png", mask)
                    #print("Size:", crop_img_size)

                    mask_negative = np.ones((crop_img_size[0], crop_img_size[1]), dtype=np.uint8) * 0
                    circle_center = (crop_img_size[1] // 2, crop_img_size[0] // 2)  # Center of the circle
                    circle_radius = 2*crop_img_size[0] // 5  # Radius of the circle
                    circle_color = 127  # Black color
                    circle_thickness = -1

                    cv2.circle(mask_negative, circle_center, circle_radius, circle_color, circle_thickness)
                    cv2.imwrite("debugging-opencv/6_mask_img_negative_index.png", mask_negative)

                    start_height += height_answer

                    crop_img_flattened = [item for sublist in crop_img for item in sublist]
                    crop_img_flattened = crop_img_flattened / max(crop_img_flattened)

                    matching_pixels = np.sum(crop_img == mask)
                    matching_pixels_negative = np.sum(crop_img == mask_negative)
                    print(f"Matching Pixels: ", matching_pixels, matching_pixels_negative)                    

                    if matching_pixels_negative > 500:
                        print("wrong answer")
                        matching_pixels = 0

                    answers_array_column.append(matching_pixels)

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
    s = 100 * points / num_of_questions
    return points, s
