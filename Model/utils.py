import base64

import cv2
import numpy as np
import sys


def stackImages(imgArray, scale, lables=[]):
    rows = len(imgArray)
    cols = len(imgArray[0])
    rowsAvailable = isinstance(imgArray[0], list)
    width = imgArray[0][0].shape[1]
    height = imgArray[0][0].shape[0]
    if rowsAvailable:
        for x in range(0, rows):
            for y in range(0, cols):
                imgArray[x][y] = cv2.resize(imgArray[x][y], (0, 0), None, scale, scale)
                if len(imgArray[x][y].shape) == 2: imgArray[x][y] = cv2.cvtColor(imgArray[x][y], cv2.COLOR_GRAY2BGR)
        imageBlank = np.zeros((height, width, 3), np.uint8)
        hor = [imageBlank] * rows
        hor_con = [imageBlank] * rows
        for x in range(0, rows):
            hor[x] = np.hstack(imgArray[x])
            hor_con[x] = np.concatenate(imgArray[x])
        ver = np.vstack(hor)
        ver_con = np.concatenate(hor)
    else:
        for x in range(0, rows):
            imgArray[x] = cv2.resize(imgArray[x], (0, 0), None, scale, scale)
            if len(imgArray[x].shape) == 2: imgArray[x] = cv2.cvtColor(imgArray[x], cv2.COLOR_GRAY2BGR)
        hor = np.hstack(imgArray)
        hor_con = np.concatenate(imgArray)
        ver = hor
    if len(lables) != 0:
        eachImgWidth = int(ver.shape[1] / cols)
        eachImgHeight = int(ver.shape[0] / rows)
        for d in range(0, rows):
            for c in range(0, cols):
                cv2.rectangle(ver, (c * eachImgWidth, eachImgHeight * d),
                              (c * eachImgWidth + len(lables[d][c]) * 13 + 27, 30 + eachImgHeight * d), (255, 255, 255),
                              cv2.FILLED)
                cv2.putText(ver, lables[d][c], (eachImgWidth * c + 10, eachImgHeight * d + 20),
                            cv2.FONT_HERSHEY_COMPLEX, 0.7, (255, 0, 255), 2)
    return ver


def reorder(myPoints):
    myPoints = myPoints.reshape((4, 2))
    #print(myPoints)
    myPointsNew = np.zeros((4, 1, 2), np.int32)
    add = myPoints.sum(1)
    myPointsNew[0] = myPoints[np.argmin(add)]  #[0,0]
    myPointsNew[3] = myPoints[np.argmax(add)]  #[w,h]
    diff = np.diff(myPoints, axis=1)
    myPointsNew[1] = myPoints[np.argmin(diff)]  #[w,0]
    myPointsNew[2] = myPoints[np.argmax(diff)]  #[h,0]

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


def splitBoxes(img):
    rows = np.vsplit(img, 5)
    boxes = []
    for r in rows:
        cols = np.hsplit(r, 5)
        for box in cols:
            boxes.append(box)
    return boxes


def drawGrid(img, questions=5, choices=20):
    secW = int(img.shape[1] / questions)
    secH = int(img.shape[0] / choices)
    data = [secW, secH]
    for i in range(0, choices + 1):
        pt1 = (0, secH * i)
        pt2 = (img.shape[1], secH * i)
        pt3 = (secW * i, 0)
        pt4 = (secW * i, img.shape[0])
        cv2.line(img, pt1, pt2, (0, 0, 0), 2)
        cv2.line(img, pt3, pt4, (0, 0, 0), 2)

        data.append(pt1)
        data.append(pt3)
    return img, data

def drawGridFullPage(img, contour, index, answers, field, questions=5, choices=20):
    index_field = index[0] + "x" + str(index[1]-1)
    print("index field", index_field)
    map = ["A", "B", "C", "D", "E"]
    if field < 3:
        answers = answers[choices*field:choices*(field+1)]
    #print("drawing answers", index, answers)
    #print(contour[1][0][1], contour[0][0][1])
    secW = int((contour[1][0][0] - contour[0][0][0]) / questions)
    secH = int((contour[2][0][1] - contour[0][0][1]) / choices)
    data = [secW, secH]
    #print("data", data)
    for i in range(0, choices + 1):
        pt1 = (contour[0][0][0], contour[0][0][1] + (secH * i))
        pt2 = (contour[1][0][0], contour[0][0][1] + (secH * i))
        cv2.line(img, pt1, pt2, (255, 0, 0), 1)
    for i in range(0, questions + 1):
        pt3 = (contour[0][0][0] + (secW * i), contour[0][0][1])
        pt4 = (contour[0][0][0] + (secW * i), contour[2][0][1])
        cv2.line(img, pt3, pt4, (255, 0, 0), 1)

    if field < 3:
        #print("drawing...")
        for i in range(0, choices):
            if answers[i] == "0":
                pass
            else:
                center = (int(contour[0][0][0] + (secW * map.index(answers[i])) + secW/2), int(contour[0][0][1] + (secH * i) + secH/2))
                #pt4 = (contour[0][0][0] + (secW * i), contour[2][0][1])
                cv2.circle(img, center, 1, (255, 0, 0), 5)

    else:
        print("drawing...")
        for i in range(0, questions):
            if i == questions - 2:
                pass
            else:
                if index_field[i] not in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]:
                    pass
                else:
                    center = (int(contour[0][0][0] + (secW * i) + secW/2), int(contour[0][0][1] + (secH * (int(index_field[i])+1)) + secH/2))
                    #pt4 = (contour[0][0][0] + (secW * i), contour[2][0][1])
                    cv2.circle(img, center, 1, (255, 0, 0), 5)
    

    return img


def showAnswers(img, myIndex, grading, ans, questions=5, choices=5):
    secW = int(img.shape[1] / questions)
    secH = int(img.shape[0] / choices)

    for x in range(0, questions):
        myAns = myIndex[x]
        cX = (myAns * secW) + secW // 2
        cY = (x * secH) + secH // 2
        if grading[x] == 1:
            myColor = (0, 255, 0)
            cv2.circle(img, (cX, cY), 50, myColor, cv2.FILLED)
        else:
            myColor = (0, 0, 255)
            cv2.circle(img, (cX, cY), 50, myColor, cv2.FILLED)

            # CORRECT ANSWER
            myColor = (0, 255, 0)
            correctAns = ans[x]
            cv2.circle(img, ((correctAns * secW) + secW // 2, (x * secH) + secH // 2),
                       20, myColor, cv2.FILLED)


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
            #print(i)
            biggest_contours.append(getCornerPoints(rect_con[i]))
            #print("aaaaa", biggest_contours[0])
    return biggest_contours


def find_contours2(img, num_rectangles):
    hardcoded_values = [
        [
            [[39, 314]],
            [[160, 314]],
            [[39, 655]],
            [[160, 655]]

        ],
        [
            [[194, 314]],
            [[316, 314]],
            [[194, 655]],
            [[316, 655]]

        ],
        [
            [[355, 314]],
            [[471, 314]],
            [[355, 655]],
            [[471, 655]]

        ],
        [
            [[137, 31]],
            [[329, 31]],
            [[137, 221]],
            [[329, 221]]

        ]
    ]
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
