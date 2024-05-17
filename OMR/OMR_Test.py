import cv2
import numpy as np
import utlis
from PIL import Image

########################################################################
webCamFeed = False
pathImage = "../data/answer_sheets/answer_sheet_2_filled.png"
cap = cv2.VideoCapture(1)
cap.set(10, 160)
#heightImg = 2339
#widthImg = 1654
#scale = 2
#heightImg = int(heightImg / scale)
#widthImg = int(widthImg / scale)
heightImg = 900
widthImg = 700
questions = 5
choices = 5
ans = [1, 2, 0, 2, 4]
rows = 15
columns = 6

ans_array = ["A", "B", "C", "D", "E", "F"]
correct_answers = ['C', 'B', 'B', 'D', 'E', 'F', 'B', 'A', 'B', 'A', 'C', 'E', 'E', 'C', 'F']

########################################################################


count = 0

while True:

    if webCamFeed:
        success, img = cap.read()
    else:
        img = cv2.imread(pathImage)
    img = cv2.resize(img, (widthImg, heightImg))  # RESIZE IMAGE
    imgFinal = img.copy()
    imgBlank = np.zeros((heightImg, widthImg, 3), np.uint8)  # CREATE A BLANK IMAGE FOR TESTING DEBUGGING IF REQUIRED
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # CONVERT IMAGE TO GRAY SCALE
    imgBlur = cv2.GaussianBlur(imgGray, (5, 5), 1)  # ADD GAUSSIAN BLUR
    imgCanny = cv2.Canny(imgBlur, 10, 170)  # APPLY CANNY

    try:
        # FIND ALL CONTOURS
        imgContours = img.copy()  # COPY IMAGE FOR DISPLAY PURPOSES
        imgBigContour = img.copy()  # COPY IMAGE FOR DISPLAY PURPOSES
        contours, hierarchy = cv2.findContours(imgCanny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)  # FIND ALL CONTOURS
        cv2.drawContours(imgContours, contours, -1, (0, 255, 0), 10)  # DRAW ALL DETECTED CONTOURS
        rectCon = utlis.rectContour(contours)  # FILTER FOR RECTANGLE CONTOURS
        biggestPoints = utlis.getCornerPoints(rectCon[0])  # GET CORNER POINTS OF THE BIGGEST RECTANGLE
        gradePoints = utlis.getCornerPoints(rectCon[1])  # GET CORNER POINTS OF THE SECOND BIGGEST RECTANGLE

        outerPoints = utlis.getCornerPoints(rectCon[0])  # TODO add a rectangle to place the page
        answersPoints1 = utlis.getCornerPoints(rectCon[0])
        answersPoints2 = utlis.getCornerPoints(rectCon[1])
        indexPoints = utlis.getCornerPoints(rectCon[2])

        if answersPoints1.size != 0 and answersPoints2.size != 0 and indexPoints.size != 0:

            # answers wrapping
            answersPoints1 = utlis.reorder(answersPoints1)  # REORDER FOR WARPING
            cv2.drawContours(imgBigContour, answersPoints1, -1, (0, 255, 0), 20)  # DRAW THE BIGGEST CONTOUR
            pts1 = np.float32(answersPoints1)  # PREPARE POINTS FOR WARP
            pts2 = np.float32([[0, 0], [widthImg, 0], [0, heightImg], [widthImg, heightImg]])  # PREPARE POINTS FOR WARP
            matrix = cv2.getPerspectiveTransform(pts1, pts2)  # GET TRANSFORMATION MATRIX
            imgWarpColored = cv2.warpPerspective(img, matrix, (widthImg, heightImg))  # APPLY WARP PERSPECTIVE

            cv2.drawContours(imgBigContour, answersPoints2, -1, (0, 255, 0), 20)  # DRAW THE BIGGEST CONTOUR
            answersPoints2 = utlis.reorder(answersPoints2)  # REORDER FOR WARPING
            ptsG1 = np.float32(answersPoints2)  # PREPARE POINTS FOR WARP
            ptsG2 = np.float32([[0, 0], [325, 0], [0, 150], [325, 150]])  # PREPARE POINTS FOR WARP
            matrixG = cv2.getPerspectiveTransform(ptsG1, ptsG2)  # GET TRANSFORMATION MATRIX
            imgGradeDisplay = cv2.warpPerspective(img, matrixG, (325, 150))  # APPLY WARP PERSPECTIVE

            # index wrapping
            indexPoints = utlis.reorder(indexPoints)  # REORDER FOR WARPING
            cv2.drawContours(imgBigContour, indexPoints, -1, (255, 0, 0), 20)  # DRAW THE BIGGEST CONTOUR
            pts1 = np.float32(indexPoints)  # PREPARE POINTS FOR WARP
            pts2 = np.float32([[0, 0], [widthImg, 0], [0, heightImg], [widthImg, heightImg]])  # PREPARE POINTS FOR WARP
            matrix = cv2.getPerspectiveTransform(pts1, pts2)  # GET TRANSFORMATION MATRIX
            imgWarpColored3 = cv2.warpPerspective(img, matrix, (widthImg, heightImg))  # APPLY WARP PERSPECTIVE

            # APPLY THRESHOLD
            imgWarpGray = cv2.cvtColor(imgWarpColored, cv2.COLOR_BGR2GRAY)  # CONVERT TO GRAYSCALE
            imgThresh = cv2.threshold(imgWarpGray, 170, 255, cv2.THRESH_BINARY_INV)[1]  # APPLY THRESHOLD AND INVERSE

            boxes = utlis.splitBoxes(imgThresh)  # GET INDIVIDUAL BOXES
            cv2.imshow("Split Test ", boxes[1])
            countR = 0
            countC = 0
            myPixelVal = np.zeros((questions, choices))  # TO STORE THE NON ZERO VALUES OF EACH BOX
            for image in boxes:
                # cv2.imshow(str(countR)+str(countC),image)
                totalPixels = cv2.countNonZero(image)
                myPixelVal[countR][countC] = totalPixels
                countC += 1
                if (countC == choices): countC = 0;countR += 1

            # FIND THE USER ANSWERS AND PUT THEM IN A LIST
            myIndex = []
            for x in range(0, questions):
                arr = myPixelVal[x]
                myIndexVal = np.where(arr == np.amax(arr))
                myIndex.append(myIndexVal[0][0])
            # print("USER ANSWERS",myIndex)

            # COMPARE THE VALUES TO FIND THE CORRECT ANSWERS
            grading = []
            for x in range(0, questions):
                if ans[x] == myIndex[x]:
                    grading.append(1)
                else:
                    grading.append(0)
            # print("GRADING",grading)
            score = (sum(grading) / questions) * 100  # FINAL GRADE
            # print("SCORE",score)

            #######################################################################################

            # drawing grid
            imgWarpColored, imgAnswersData = utlis.drawGrid(imgWarpColored)  # DRAW GRID
            #print(imgAnswersData)

            # search for all grid areas, find the most colored ones, add threshold
            heightAnswer = imgAnswersData[1]
            widthAnswer = imgAnswersData[0]

            answers_array = []
            start_height = 0
            for row in range(rows):
                answers_array_row = []
                start_width = 0
                for col in range(columns):

                    crop_img = imgThresh[start_height:start_height + heightAnswer, start_width:start_width + widthAnswer]
                    start_width += widthAnswer

                    cv2.imshow("cropped", crop_img)
                    average_color = crop_img.mean(axis=0).mean(axis=0)
                    #print(average_color)
                    answers_array_row.append(average_color)
                answers_array.append(answers_array_row)
                start_height += heightAnswer
            #print(answers_array)

            answers = []
            for question in answers_array:
                answers.append(ans_array[question.index(max(question))])
            #print(answers)
            print(correct_answers, answers)
            points, score = utlis.score(correct_answers, answers)
            print(points)
            print(score, "%")

            #######################################################################################

            imgRawDrawings = np.zeros_like(imgWarpColored)  # NEW BLANK IMAGE WITH WARP IMAGE SIZE
            utlis.showAnswers(imgRawDrawings, myIndex, grading, ans)  # DRAW ON NEW IMAGE
            invMatrix = cv2.getPerspectiveTransform(pts2, pts1)  # INVERSE TRANSFORMATION MATRIX
            imgInvWarp = cv2.warpPerspective(imgRawDrawings, invMatrix, (widthImg, heightImg))  # INV IMAGE WARP

            # DISPLAY GRADE
            imgRawGrade = np.zeros_like(imgWarpColored, np.uint8)  # NEW BLANK IMAGE WITH GRADE AREA SIZE
            cv2.putText(imgRawGrade, str(int(score)) + "%", (70, 200)
                        , cv2.FONT_HERSHEY_COMPLEX, 3, (155, 255, 155), 3)  # ADD THE GRADE TO NEW IMAGE
            invMatrixG = cv2.getPerspectiveTransform(ptsG2, ptsG1)  # INVERSE TRANSFORMATION MATRIX
            imgInvGradeDisplay = cv2.warpPerspective(imgRawGrade, invMatrixG, (widthImg, heightImg))  # INV IMAGE WARP

            # SHOW ANSWERS AND GRADE ON FINAL IMAGE
            imgFinal = cv2.addWeighted(imgFinal, 1, imgInvWarp, 1, 0)
            imgFinal = cv2.addWeighted(imgFinal, 1, imgInvGradeDisplay, 1, 0)

            # IMAGE ARRAY FOR DISPLAY
            imageArray = ([img, imgGray, imgCanny, imgContours],
                          [imgBigContour, imgThresh, imgWarpColored, imgFinal])
            cv2.imshow("Final Result", imgFinal)
    except:
        imageArray = ([img, imgGray, imgCanny, imgContours],
                      [imgBlank, imgBlank, imgBlank, imgBlank])

    # LABELS FOR DISPLAY
    labels = [["Original", "Gray", "Edges", "Contours"],
              ["Biggest Contour", "Threshold", "Warped", "Final"]]

    stackedImage = utlis.stackImages(imageArray, 0.5, labels)
    cv2.imshow("Result", stackedImage)

    # SAVE IMAGE WHEN 's' key is pressed
    if cv2.waitKey(1) & 0xFF == ord('s'):
        cv2.imwrite("Scanned/myImage" + str(count) + ".jpg", imgFinal)
        cv2.rectangle(stackedImage, ((int(stackedImage.shape[1] / 2) - 230), int(stackedImage.shape[0] / 2) + 50),
                      (1100, 350), (0, 255, 0), cv2.FILLED)
        cv2.putText(stackedImage, "Scan Saved", (int(stackedImage.shape[1] / 2) - 200, int(stackedImage.shape[0] / 2)),
                    cv2.FONT_HERSHEY_DUPLEX, 3, (0, 0, 255), 5, cv2.LINE_AA)
        cv2.imshow('Result', stackedImage)
        cv2.waitKey(300)
        count += 1
