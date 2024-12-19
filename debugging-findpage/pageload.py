
import cv2
import numpy as np


def change_brightness(input_image, contrast = 1.0, brightness=30):
    ''' input_image:  color or grayscale image
        contrast:  1 gives original image, # Contrast control (1.0-3.0)
        brightness:  -255 (all black) to +255 (all white)

        returns image of same type as input_image but with
        brightness adjusted'''
    img = input_image.copy()
    cv2.convertScaleAbs(img, img, contrast, brightness)
    return img

# Wczytaj obraz
image = cv2.imread("img_8.png")

# Create the sharpening kernel
# kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
# image = cv2.filter2D(image, -1, kernel)

# image = cv2.Laplacian(image, cv2.CV_8UC3)

# normalized_img = np.zeros((800, 800))
# image = cv2.normalize(image, normalized_img, 0, 255, cv2.NORM_MINMAX)
# image = cv2.GaussianBlur(image, (3, 3), 1)
# image = change_brightness(image, 1, -30)

if image is None:
    raise ValueError("Image not loaded. Please check the image path or URL.")

# Sprawdź liczbę kanałów w obrazie
if len(image.shape) == 2:  # Obraz w skali szarości
    image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
elif image.shape[2] == 4:  # Obraz RGBA
    image = cv2.cvtColor(image, cv2.COLOR_RGBA2BGR)

# Konwertuj obraz do skali szarości
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Zastosuj progowanie adaptacyjne - znacząco poprawia detekcję markerów
gray = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 91, 5)

cv2.imshow('Gray Image', gray)

# Zdefiniuj słownik ArUco i parametry detekcji
aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_250)
parameters = cv2.aruco.DetectorParameters()

# Utwórz detektor znaczników ArUco
detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)

# Wykryj znaczniki ArUco
corners, ids, rejected = detector.detectMarkers(gray)

cv2.aruco.drawDetectedMarkers(image, corners, ids)
# Sprawdź, czy wykryto znaczniki
if ids is not None and len(ids) >= 4:
    # Posortuj wykryte znaczniki na podstawie ich ID
    ids = ids.flatten()
    sorted_indices = np.argsort(ids)
    corners = [corners[i] for i in sorted_indices]


    # Pobierz cztery znaczniki (lewy górny, prawy górny, prawy dolny, lewy dolny)
    selected_corners = [corners[0][0][0], corners[1][0][1], corners[2][0][3], corners[3][0][2]]
    print(sorted_indices, ids, selected_corners)
    # Utwórz macierz perspektywy
    src_points = np.float32(selected_corners)  # Wykryte punkty znaczników
    dst_points = np.float32([[0, 0], [600, 0], [0, 800], [600, 800]])  # Prostokąt docelowy
    matrix = cv2.getPerspectiveTransform(src_points, dst_points)

    # Przekształcenie perspektywy (wycięcie obszaru strony)
    warped_image = cv2.warpPerspective(image, matrix, (600, 800))

    # Wyświetl wynik


    cv2.imshow('Warped Image', warped_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
else:
    image = cv2.resize(image, (600, 800))
    cv2.imshow('Original Image', image)
    cv2.waitKey(0)
    print("Not enough ArUco markers detected to perform perspective transform.")


