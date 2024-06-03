import cv2
import numpy as np
import utlis
import USOS_utils as usos_utils
import statistics
import time

# TODO ###################
# 3. Number of questions
# 4. Video capture
# 5. wybór grupy
# 6. flip the answers if the right one is bigger

########################################################################
webcam_feed = False
path_to_image = "../data/answer_sheets/answer_sheet_5_3.png"

cap = cv2.VideoCapture(0)
cap.set(10, 160)

heightImg = 2339
widthImg = 1654
scale = 2
heightImg = int(heightImg / scale)
widthImg = int(widthImg / scale)

rows = 15
columns = 6
num_answer_fields = 2

ans_array = ["A", "B", "C", "D", "E", "F"]
#correct_answers = ['C', 'B', 'B', 'D', 'E', 'F', 'B', 'A', 'B', 'A', 'C', 'E', 'E', 'C', 'F', 'A', 'B', 'C', 'D', 'E', 'F', 'D', 'D', 'B', 'C', 'D', 'E', 'A', 'A', 'C']

points_to_check = [[15,11], [15,489], [685,11], [693,489], [15,22], [25,11]]
white_thresh = 200


########################################################################


def load_image(path, webcam_feed):
    if webcam_feed:
        success, img = cap.read()
    else:
        img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    return img


def remove_shadows(img):
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


def preprocess_image(img):
    img = cv2.resize(img, (widthImg, heightImg))
    img_blur = cv2.GaussianBlur(img, (5, 5), 1)
    return img_blur


def find_page(img):
    img_copy = img
    # finds biggest contour in image
    contour = utlis.find_contours(img, 1)
    # print(len(contour))

    # transform
    if contour != []:
        image_warped = utlis.image_warping(contour[0], img, 500, 700)
    else:
        print("No contour found")
    # points to check
    '''
    image_warped[15][11] = 255

    image_warped[25][11] = 255
    image_warped[15][489] = 255
    image_warped[685][489] = 255
    image_warped[685][11] = 255
    '''
    # print(image_warped[7][5])
    # print(image_warped[-10][-10])

    wrong_format = False
    # check if the found contour is the answer sheet and if the orientation is correct
    i = -1
    for point in points_to_check:
        i += 1
        #print(image_warped[point[0], point[1]])
        if image_warped[point[0], point[1]] < white_thresh:
            #print("Correct format")
            continue
        else:
            wrong_format = True
            if i == 4 or i == 5:
                #print("Wrong orientation")
                break
            #print("Not an answer sheet. Quitting", point)
            break

    if wrong_format:
        return image_warped
        print("AAAA")
    return image_warped[5:-5,5:-5]


def apply_threshold(img):
    img_thresh = cv2.threshold(img, 170, 255, cv2.THRESH_BINARY_INV)[1]

    return img_thresh


def draw_grid(img, is_index):
    if not is_index:
        return utlis.drawGrid(img)
    else:
        return utlis.drawGrid(img, questions=8, choices=11)


def get_answers(img, img_answers_data, is_index=False):
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


def omr_read_correct_answers():
    # function reads correct answers from an answer sheet
    img = load_image(path_to_image, webcam_feed)
    img = find_page(img)
    #cv2.imshow("label", img)
    img_no_shadows = remove_shadows(img)
    img_preprocessed = preprocess_image(img_no_shadows)

    img_contours = utlis.find_contours(img_preprocessed, num_answer_fields + 1)

    images_warped = []
    for contour in img_contours:
        images_warped.append(utlis.image_warping(contour, img_preprocessed, widthImg, heightImg))

    images_threshold = []
    for warped_image in images_warped:
        images_threshold.append(apply_threshold(warped_image))

    images_grid = []
    i = 0
    for threshold_image in images_threshold:
        if i % (num_answer_fields + 1) == num_answer_fields:
            images_grid.append(draw_grid(threshold_image, is_index=True))
            i = 0
        else:
            images_grid.append(draw_grid(threshold_image, is_index=False))  # TODO delete unnecessary data
            i += 1
    #cv2.imshow("label3", images_grid[2][0])
    images_answers = []
    i = 0
    for grid in images_grid:
        if i % (num_answer_fields + 1) == num_answer_fields:
            images_answers.append(get_answers(grid[0], grid[1], is_index=True))
            i = 0
        else:
            images_answers.append(get_answers(grid[0], grid[1]))
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
    print(index_answer)
    index_answers = []
    for char in index_answer:
        index_answers.append(str(char.index(max(char))-2))
    index_txt = "".join(index_answers)

    group_answer = images_answers[-1][-1]
    group = group_answer.index(max(group_answer))
    print("Grupa:",group)

    cv2.waitKey(0)

    return index_txt, full_answers, group


def omr_grade(correct_answers):
    # function grades answers based on the correct answers in the argument
    img = load_image(path_to_image, webcam_feed)
    img = find_page(img)
    #cv2.imshow("label", img)
    img_no_shadows = remove_shadows(img)
    img_preprocessed = preprocess_image(img_no_shadows)

    img_contours = utlis.find_contours(img_preprocessed, num_answer_fields + 1)

    images_warped = []
    for contour in img_contours:
        images_warped.append(utlis.image_warping(contour, img_preprocessed, widthImg, heightImg))

    images_threshold = []
    for warped_image in images_warped:
        images_threshold.append(apply_threshold(warped_image))

    images_grid = []
    i = 0
    for threshold_image in images_threshold:
        if i % (num_answer_fields + 1) == num_answer_fields:
            images_grid.append(draw_grid(threshold_image, is_index=True))
            i = 0
        else:
            images_grid.append(draw_grid(threshold_image, is_index=False))  # TODO delete unnecessary data
            i += 1

    images_answers = []
    i = 0
    for grid in images_grid:
        if i % (num_answer_fields + 1) == num_answer_fields:
            images_answers.append(get_answers(grid[0], grid[1], is_index=True))
            i = 0
        else:
            images_answers.append(get_answers(grid[0], grid[1]))
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
    points, score = utlis.score(correct_answers, full_answers)
    print("\nOdpowiedzi:         ", full_answers)

    # read the index
    index_answer = images_answers[-1][:-2]
    index_answers = []
    for char in index_answer:
        index_answers.append(str(char.index(max(char))-2))
    index_txt = "".join(index_answers)

    group_answer = images_answers[-1][-1]
    group = group_answer.index(max(group_answer))
    print("Grupa:",group)


    cv2.waitKey(0)

    return index_txt, score, group


_, answers, group_answers = omr_read_correct_answers()
print("\nPoprawne odpowiedzi:", answers)

index, score, group = omr_grade(answers)
print("\nIndeks:", index, "\nWynik:", score, "\nGrupa:", group)

data = usos_utils.import_data()
export_csv = usos_utils.export_data({index: score}, data, score)
print(export_csv)
