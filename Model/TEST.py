import cv2

cam_index = 0  # Sprawdź indeks kamery, zmień na 1 lub inny, jeśli 0 nie działa
cap = cv2.VideoCapture(cam_index)  # lub CAP_MSMF

if not cap.isOpened():
    print("Błąd: Kamera nie może zostać otwarta.")
else:
    ret, frame = cap.read()
    if ret:
        cv2.imshow("Podgląd kamery", frame)
        cv2.waitKey(0)
    else:
        print("Błąd: Nie udało się przechwycić obrazu.")

    cap.release()
    cv2.destroyAllWindows()