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
        if area > 50:
            peri = cv2.arcLength(i, True)
            approx = cv2.approxPolyDP(i, 0.09 * peri, True)
            if len(approx) == 4:
                rectCon.append(i)
    rectCon = sorted(rectCon, key=cv2.contourArea, reverse=True)
    return rectCon


def rectContourTables(contours):
    rectCon = []
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
    #print("index field", index_field)
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

    #print("biggest contours:", biggest_contours)
    return biggest_contours


def find_contours_page(img, num_rectangles):
    if img is None:
        raise ValueError("Image not loaded. Please check the image path or URL.")

    # Sprawdź liczbę kanałów w obrazie
    if len(img.shape) == 2:  # Obraz w skali szarości
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    elif img.shape[2] == 4:  # Obraz RGBA
        img = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)

    # Konwertuj obraz do skali szarości
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Zdefiniuj słownik ArUco i parametry detekcji
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_250)
    parameters = cv2.aruco.DetectorParameters()

    # Utwórz detektor znaczników ArUco
    detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)


    # if aruco detector fails to detect markers, try to do adaptive thresholding
    warped_image = detectAruco(detector, gray, img)

    for i in range(51, 152, 10):
        if warped_image is not None:
            break
        # Zastosuj progowanie adaptacyjne - znacząco poprawia detekcję markerów
        imgThresholded = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, i, 5)
        warped_image = detectAruco(detector, imgThresholded, img)
    return warped_image

def detectAruco(arucoDetector, image, image2warp):
    # Wykryj znaczniki ArUco
    corners, ids, rejected = arucoDetector.detectMarkers(image)

    # Sprawdź, czy wykryto znaczniki
    if ids is not None and len(ids) >= 4:
        # Posortuj wykryte znaczniki na podstawie ich ID
        ids = ids.flatten()
        sorted_indices = np.argsort(ids)
        corners = [corners[j] for j in sorted_indices]

        # Pobierz cztery znaczniki (lewy górny, prawy górny, prawy dolny, lewy dolny)
        selected_corners = [corners[0][0][0], corners[1][0][1], corners[2][0][3], corners[3][0][2]]
        print(sorted_indices, ids, selected_corners)
        # Utwórz macierz perspektywy
        src_points = np.float32(selected_corners)  # Wykryte punkty znaczników
        dst_points = np.float32([[0, 0], [600, 0], [0, 800], [600, 800]])  # Prostokąt docelowy
        matrix = cv2.getPerspectiveTransform(src_points, dst_points)

        # Przekształcenie perspektywy (wycięcie obszaru strony) ale z oryginalnego obrazu
        return cv2.warpPerspective(image2warp, matrix, (600, 800))
    elif ids is not None and len(ids) == 3:
        # Posortuj wykryte znaczniki na podstawie ich ID
        ids = ids.flatten()
        sorted_indices = np.argsort(ids)
        corners = [corners[j] for j in sorted_indices]
        print("sorted indices: " +  str(sorted_indices), "ids: " + str(ids))
        # Pobierz cztery znaczniki (lewy górny, prawy górny, prawy dolny, lewy dolny)
        selected_corners = [corners[0][0][0], corners[1][0][1], corners[2][0][3], corners[3][0][2]]
        print(sorted_indices, ids, selected_corners)
        # Utwórz macierz perspektywy
        src_points = np.float32(selected_corners)  # Wykryte punkty znaczników
        dst_points = np.float32([[0, 0], [600, 0], [0, 800], [600, 800]])  # Prostokąt docelowy
        matrix = cv2.getPerspectiveTransform(src_points, dst_points)

        # Przekształcenie perspektywy (wycięcie obszaru strony) ale z oryginalnego obrazu
        return cv2.warpPerspective(image2warp, matrix, (600, 800))
    else:
        return None


def createRectangleImage(height, width):
    # Create a blank image
    image = np.ones((height, width, 3), dtype=np.uint8) * 255

    # Define the top-left and bottom-right points of the rectangle
    top_left = (0, 0)
    bottom_right = (width, height)

    # Define the color (BGR) and thickness of the rectangle
    color = (0, 0, 0)
    thickness = 2  # Thickness of 2 pixels

    # Draw the rectangle on the image
    cv2.rectangle(image, top_left, bottom_right, color, thickness)

    # Save or display the result
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    cv2.imwrite('debugging-opencv/rectangle_image.png', image)
    return image


def find_contours_tables(img, num_rectangles, index=False):
    if len(img.shape)==3:    
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img_contours = img.copy()
    cv2.imwrite("debugging-opencv/3bb_matchTemplate.png", img)

    contours = None
    top_left = (0, 0)
    bottom_right = (0, 0)
    best_max_value = 0
    best_width_offset = 0

    # TODO this two loops need some cleanup in code
    for i in range(-5, 5):
        if not index:
            img_rectangle = createRectangleImage(390, 149 + i)
        else:
            img_rectangle = createRectangleImage(216, 237 + i)
        # Apply template Matching
        res = cv2.matchTemplate(img, img_rectangle, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        # Store best match
        if max_val > best_max_value:
            best_max_value = max_val
            best_width_offset = i
    for j in range(-5, 5):
        if not index:
            img_rectangle = createRectangleImage(390 + j, 149 + best_width_offset)
        else:
            img_rectangle = createRectangleImage(216 + j, 237 + best_width_offset)
        # Apply template Matching
        res = cv2.matchTemplate(img, img_rectangle, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        # Store best match
        if max_val >= best_max_value: #TODO >= koniecznie wyliczenie naroznikow musi sie wykonac chociaz 1 raz!!!
            best_max_value = max_val
            top_left = max_loc
            h, w = img_rectangle.shape
            bottom_right = (top_left[0] + w, top_left[1] + h)
            contours = np.array([[
                [[top_left[0], top_left[1]]],
                [[top_left[0], bottom_right[1]]],
                [[bottom_right[0], top_left[1]]],
                [[bottom_right[0], bottom_right[1]]]
            ]])

    # Draw clear rectangle for perfect contour detection in next step
    print("top left", top_left, "bottom right", bottom_right)
    cv2.rectangle(img,  top_left, bottom_right, 0, 2)
    cv2.imwrite("debugging-opencv/3b_matchTemplate.png", img)
    cv2.imwrite("debugging-opencv/3c_img_contours2.png", img_contours)

    return contours


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


def change_brightness(input_image, contrast=1, brightness=30):
    ''' input_image:  color or grayscale image
        contrast:  1 gives original image, # Contrast control (1.0-3.0)
        brightness:  -255 (all black) to +255 (all white)

        returns image of same type as input_image but with
        brightness adjusted
    '''
    img = input_image.copy()
    cv2.convertScaleAbs(img, img, contrast, brightness)
    return img


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
            #print("cnt:", cnt)
            xes = [cnt[0][0][0], cnt[1][0][0], cnt[2][0][0], cnt[3][0][0]]
            xes.sort()
            yes = [cnt[0][0][1], cnt[1][0][1], cnt[2][0][1], cnt[3][0][1]]
            yes.sort()
            xleft = (xes[0] + xes[1]) / 2
            xright = self.getWidth() - (xes[2] + xes[3]) / 2
            ytop = (yes[0] + yes[1]) / 2
            ybottom = self.getHeight() - (yes[2] + yes[3]) / 2

            self.pt_top_left = [round(self.pt_top_left[0] + xleft), round(self.pt_top_left[1] + ytop)]
            self.pt_bottom_right = [round(self.pt_bottom_right[0] - xright), round(self.pt_bottom_right[1] - ybottom)]

        else:
            print("updateFromRelativeContour - ERROR: cnt is not a numpy array")
