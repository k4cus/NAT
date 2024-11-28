import base64
import cv2
import numpy as np


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
    for i in contours:
        area = cv2.contourArea(i)
        #print("Area:" ,area)
        # exit()
        if area > 50:
            peri = cv2.arcLength(i, True)
            #print("Peri:", peri)
            approx = cv2.approxPolyDP(i, 0.09 * peri, True)
            #print("Approx:", approx)
            if len(approx) == 4:
                rectCon.append(i)
    rectCon = sorted(rectCon, key=cv2.contourArea, reverse=True)
    return rectCon

def rectContourTables(contours):
    rectCon = []
    for i in contours:
        area = cv2.contourArea(i)
        print("Area:" ,area)
        # exit()
        if area > 50:
            peri = cv2.arcLength(i, True)
            print("Peri:", peri)
            approx = cv2.approxPolyDP(i, 0.09 * peri, True)
            print("Approx:", approx)
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
    letters = ["A", "B", "C", "D", "E"]
    if field < 3:
        answers = answers[choices * field:choices * (field + 1)]

    secW = ((contour[1][0][0] - contour[0][0][0]) / questions)
    secH = ((contour[2][0][1] - contour[0][0][1]) / choices)

    for i in range(0, choices + 1):
        pt1 = (contour[0][0][0], contour[0][0][1] + round(secH * i))
        pt2 = (contour[1][0][0], contour[0][0][1] + round(secH * i))
        cv2.line(img, pt1, pt2, (255, 0, 0), 1)
    for i in range(0, questions + 1):
        pt3 = (contour[0][0][0] + round(secW * i), contour[0][0][1])
        pt4 = (contour[0][0][0] + round(secW * i), contour[2][0][1])
        cv2.line(img, pt3, pt4, (255, 0, 0), 1)

    if field < 3:
        for i in range(0, choices):
            if answers[i] == "0":
                pass
            else:
                center = (round(contour[0][0][0] + (secW * letters.index(answers[i])) + secW / 2), round(contour[0][0][1] + (secH * i) + secH / 2))
                cv2.circle(img, center, 1, (255, 0, 0), 5)

    else:
        for i in range(0, questions):
            if i == questions - 2:
                pass
            else:
                if index_field[i] not in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]:
                    pass
                else:
                    center = (
                        round(contour[0][0][0] + (secW * i) + secW / 2), round(contour[0][0][1] + (secH * (int(index_field[i]) + 1)) + secH / 2))
                    cv2.circle(img, center, 1, (255, 0, 0), 5)

    return img


def score(correct, answers):
    points = 0
    num_of_questions = len(correct)
    for question in range(num_of_questions):
        if correct[question] == answers[question]:
            points += 1
    s = 100 * points / num_of_questions
    return points, s


def find_contours(img, num_rectangles):
    img_canny = cv2.Canny(img, 10, 230)
    cv2.imwrite("debugging-opencv/canny.png", img_canny)
    img_contours = img.copy()
    contours, hierarchy = cv2.findContours(img_canny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(img_contours, contours, -1, (0, 255, 0), 10)
    rect_con = rectContour(contours)

    biggest_contours = []
    if num_rectangles > len(rect_con):
        num_rectangles = len(rect_con)
    if len(rect_con) > 0:
        for i in range(num_rectangles):
            biggest_contours.append(getCornerPoints(rect_con[i]))
    return biggest_contours

def find_contours_tables(img, num_rectangles):
    img_canny = cv2.Canny(img, 10, 130)
    cv2.imwrite("debugging-opencv/3b_canny_table.png", img_canny)
    img_contours = img.copy()
    size = img_contours.size
    print("size:", size)
    # kernel = np.ones((5, 5), np.uint8)
    # kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5,1))
    kernel = np.zeros((15,15), dtype=np.uint8)
    kernel[0:14,14] = 1
    kernel[0,0:14] = 1
    img_morph = cv2.morphologyEx(img_canny, cv2.MORPH_CLOSE, kernel)
    contours, hierarchy = cv2.findContours(img_morph, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    rect_con = rectContourTables(contours)
    cv2.drawContours(img_contours, rect_con, -1, (0, 255, 0), 2)
    cv2.imwrite("debugging-opencv/3b_img_contours.png", img_contours)
    exit()
    biggest_contours = []
    print("Znalezionych:", len(rect_con))
    if num_rectangles > len(rect_con):
        num_rectangles = len(rect_con)
    if len(rect_con) > 0:
        for i in range(num_rectangles):
            biggest_contours.append(getCornerPoints(rect_con[i]))
    return biggest_contours

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

    def updateFromRelativeContour(self, cnt):
        # updates position of points and width+height based on the new relative contour dimensions detected on the cut out image
        # and passed here
        # calculate corrections
        # point are out of order so we must sort x and y coordinates
        if isinstance(cnt, np.ndarray):
            xes = [cnt[0][0][0], cnt[1][0][0], cnt[2][0][0], cnt[3][0][0]]
            xes.sort()
            yes = [cnt[0][0][1], cnt[1][0][1], cnt[2][0][1], cnt[3][0][1]]
            yes.sort()
            xleft = (xes[0] + xes[1]) / 2
            xright = self.getWidth() - (xes[2] + xes[3]) / 2
            ytop = (yes[0] + yes[1]) / 2
            ybottom = self.getHeight() - (yes[2] + yes[3]) / 2
            # print("before update: ", self.pt_top_left)
            # print("before update: ", self.pt_bottom_right)
            self.pt_top_left = [round(self.pt_top_left[0] + xleft), round(self.pt_top_left[1] + ytop)]
            self.pt_bottom_right = [round(self.pt_bottom_right[0] - xright), round(self.pt_bottom_right[1] - ybottom)]
            # print("after update: ", self.pt_top_left)
            # print("after update: ", self.pt_bottom_right)
            # print(type(cnt))
            # print("cnt:", cnt)
            # print("xleft:", xleft)
            # print("xright:", xright)
            # print("ytop:", ytop)
            # print("ybottom:", ybottom)
        else:
            print("updateFromRelativeContour - ERROR: cnt is not a numpy array")
