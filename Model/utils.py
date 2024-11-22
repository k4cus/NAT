import base64

import cv2
import numpy as np
import sys


def reorder(myPoints):
    myPoints = myPoints.reshape((4, 2))
    myPointsNew = np.zeros((4, 1, 2), np.int32)
    add = myPoints.sum(1)
    myPointsNew[0] = myPoints[np.argmin(add)]  # [0,0]
    myPointsNew[3] = myPoints[np.argmax(add)]  # [w,h]
    diff = np.diff(myPoints, axis=1)
    myPointsNew[1] = myPoints[np.argmin(diff)]  # [w,0]
    myPointsNew[2] = myPoints[np.argmax(diff)]  # [h,0]

    return myPointsNew


def rectContour(contours):
    rectCon = []
    max_area = 0
    for i in contours:
        area = cv2.contourArea(i)
        if area > 50:
            peri = cv2.arcLength(i, True)
            approx = cv2.approxPolyDP(i, 0.02 * peri, True)
            if len(approx) == 4:
                rectCon.append(i)
    rectCon = sorted(rectCon, key=cv2.contourArea, reverse=True)
    return rectCon


def getCornerPoints(cont):
    peri = cv2.arcLength(cont, True)
    approx = cv2.approxPolyDP(cont, 0.02 * peri, True)
    return approx


def drawGrid(img, questions=5, choices=20):
    secW = (img.shape[1] / questions)
    secH = (img.shape[0] / choices)
    data = [secW, secH]
    for i in range(0, choices + 1):
        pt1 = (0, round(secH * i))
        pt2 = (img.shape[1], round(secH * i))
        pt3 = (round(secW * i), 0)
        pt4 = (round(secW * i), img.shape[0])
        cv2.line(img, pt1, pt2, (0, 0, 0), 2)
        cv2.line(img, pt3, pt4, (0, 0, 0), 2)
        data.append(pt1)
        data.append(pt3)
    return img, data


def drawGridFullPage(img, contour, index, answers, field, questions=5, choices=20):
    index_field = index[0] + "x" + str(index[1] - 1)
    print("index field", index_field)
    map = ["A", "B", "C", "D", "E"]
    if field < 3:
        answers = answers[choices * field:choices * (field + 1)]

    secW = int((contour[1][0][0] - contour[0][0][0]) / questions)
    secH = int((contour[2][0][1] - contour[0][0][1]) / choices)

    for i in range(0, choices + 1):
        pt1 = (contour[0][0][0], contour[0][0][1] + (secH * i))
        pt2 = (contour[1][0][0], contour[0][0][1] + (secH * i))
        cv2.line(img, pt1, pt2, (255, 0, 0), 1)
    for i in range(0, questions + 1):
        pt3 = (contour[0][0][0] + (secW * i), contour[0][0][1])
        pt4 = (contour[0][0][0] + (secW * i), contour[2][0][1])
        cv2.line(img, pt3, pt4, (255, 0, 0), 1)

    if field < 3:
        for i in range(0, choices):
            if answers[i] == "0":
                pass
            else:
                center = (int(contour[0][0][0] + (secW * map.index(answers[i])) + secW / 2), int(contour[0][0][1] + (secH * i) + secH / 2))
                cv2.circle(img, center, 1, (255, 0, 0), 5)

    else:
        for i in range(0, questions):
            if i == questions - 2:
                pass
            else:
                if index_field[i] not in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]:
                    pass
                else:
                    center = (int(contour[0][0][0] + (secW * i) + secW / 2), int(contour[0][0][1] + (secH * (int(index_field[i]) + 1)) + secH / 2))
                    cv2.circle(img, center, 1, (255, 0, 0), 5)

    return img


def score(correct, answers):
    points = 0
    num_of_questions = len(correct)
    for question in range(num_of_questions):
        if correct[question] == answers[question]:
            points += 1
    score = 100 * points / num_of_questions
    return points, score


def find_contours(img, num_rectangles):
    img_canny = cv2.Canny(img, 10, 230)
    cv2.imwrite("debugging-opencv/canny.png", img_canny)
    img_contours = img.copy()
    contours, hierarchy = cv2.findContours(img_canny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    cv2.drawContours(img_contours, contours, -1, (0, 255, 0), 10)
    rect_con = rectContour(contours)

    biggest_contours = []
    if num_rectangles > len(rect_con):
        num_rectangles = len(rect_con)
    if len(rect_con) > 0:
        for i in range(num_rectangles):
            biggest_contours.append(getCornerPoints(rect_con[i]))
    return biggest_contours


def find_contours2(img, num_rectangles):
    tableWithIndex = cropRectangle([260, 50], [670, 454])
    hardcoded_values = [
        [
            [[70, 625]],
            [[329, 625]],
            [[70, 1320]],
            [[329, 1320]]

        ],
        [
            [[380, 625]],
            [[642, 625]],
            [[380, 1320]],
            [[642, 1320]]

        ],
        [
            [[692, 625]],
            [[956, 625]],
            [[692, 1320]],
            [[956, 1320]]

        ]
    ]
    # print("1: ", hardcoded_values)
    # print("2: ", tableWithIndex.getContour())
    hardcoded_values.append(tableWithIndex.getContour())
    # print("3: ", hardcoded_values)
    hardcoded_values = np.array(hardcoded_values)
    return hardcoded_values


def find_contours3(img, num_rectangles):
    hardcoded_values = [
        [
            [[39, 314]],
            [[160, 314]],
            [[160, 655]],
            [[39, 655]]

        ],
        [
            [[194, 314]],
            [[316, 314]],
            [[316, 655]],
            [[194, 655]]

        ],
        [
            [[355, 314]],
            [[471, 314]],
            [[471, 655]],
            [[355, 655]],

        ],
        [
            [[137, 31]],
            [[329, 31]],
            [[329, 221]],
            [[137, 221]],

        ]
    ]
    hardcoded_values = np.array(hardcoded_values)
    return hardcoded_values


def image_warping(img_contours, img, widthImg, heightImg):
    if img_contours.size == 0:
        print("Contour size is zero.")
        return 0
    else:
        img_contours = reorder(img_contours)
        pts1 = np.float32(img_contours)
        pts2 = np.float32([[0, 0], [widthImg, 0], [0, heightImg], [widthImg, heightImg]])
        matrix = cv2.getPerspectiveTransform(pts1, pts2)
        image_warped = cv2.warpPerspective(img, matrix, (widthImg, heightImg))

        return image_warped


def to_base64(image):
    base64_image = cv2.imencode('.png', image)[1]
    base64_image = base64.b64encode(base64_image).decode('utf-8')
    return base64_image


def base64_empty_image(width, height):
    empty_image = np.zeros((width, height, 3), dtype=np.uint8) + 128
    return to_base64(empty_image)


class cropRectangle:
    def __init__(self, pt_top_left, pt_bottom_right):
        self.pt_top_left = pt_top_left
        self.pt_bottom_right = pt_bottom_right

    def getWidth(self):
        return self.pt_bottom_right[0] - self.pt_top_left[0]

    def getHeight(self):
        return self.pt_bottom_right[1] - self.pt_top_left[1]

    def getContour(self):
        return [
            [[self.pt_top_left[0], self.pt_top_left[1]]],
            [[self.pt_bottom_right[0], self.pt_top_left[1]]],
            [[self.pt_bottom_right[0], self.pt_bottom_right[1]]],
            [[self.pt_top_left[0], self.pt_bottom_right[1]]]
        ]
