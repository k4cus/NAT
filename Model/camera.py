import cv2
import subprocess
import numpy as np


class camera:

    def __init__(self, controller):
        self.controller = controller
        self.cameraInputIndex = 'Microsoft® LifeCam HD-5000'
        self.camera_index = 'Microsoft® LifeCam HD-5000'
        self.video_size = "640x480"
        self.fps = 30
        self.cv2 = cv2
        self.vid = None
        self.command = [
            "ffmpeg",
            "-f", "dshow",  # Format dla Windowsa
            "-framerate", str(self.fps),
            "-video_size", self.video_size,
            "-i", f"video={self.camera_index}",
            "-pix_fmt", "bgr24",  # Format obrazu zgodny z OpenCV
            "-f", "rawvideo",  # Surowy format wideo
            "-"
        ]

    def initialize(self):
        #self.cameraInputIndex = self.controller.getSettings()[
           # 'cameraIndex']  # this must be executed after model is initialized
        self.cameraInputIndex = 'Microsoft® LifeCam HD-5000'

    def getCameraInputIndex(self):
        return self.cameraInputIndex

    def setCameraInputIndex(self, index):
        # check if input is valid
        isInputValid = self.checkCameraIndex(index)
        if isInputValid:
            self.cameraInputIndex = index
            self.controller.setSetting('cameraIndex', int(index))
        return isInputValid  # message to display in view

    def checkCameraIndex(self, index):
        # check if camera index is valid
        vid = self.cv2.VideoCapture(int(index))
        isOpened = vid.isOpened()
        vid.release()
        return isOpened

    def openCamera(self):
        self.process = subprocess.Popen(self.command, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, bufsize=10 ** 8)



    def closeCamera(self):
        if self.vid is not None and self.vid.isOpened():
            self.vid.release()

    def isCameraOpen(self):
        if self.vid is not None and self.vid.isOpened():
            return True
        return False

    def getFrame(self):
        if self.process is not None:
            while True:
                raw_frame = self.process.stdout.read(640 * 480 * 3)  # 640x480 w bgr24 = 3 bajty na piksel
                if not raw_frame:
                    pass

                # Konwersja klatki na numpy array
                frame = np.frombuffer(raw_frame, np.uint8).reshape((480, 640, 3))

                # Wyświetlenie klatki (opcjonalne)

                return frame



        return None



if __name__=="__main__":
    import subprocess
    import numpy as np
    import cv2


    # Parametry FFmpeg i kamerki

    camera_index = 'Microsoft® LifeCam HD-5000'  # Zmień na nazwę swojej kamerki (ffmpeg -list_devices true -f dshow -i dummy)
    video_size = "640x480"  # Rozdzielczość obrazu
    fps = 30  # Liczba klatek na sekundę

    # Polecenie FFmpeg dla Windowsa
    command = [
        "ffmpeg",
        "-f", "dshow",  # Format dla Windowsa
        "-framerate", str(fps),
        "-video_size", video_size,
        "-i", f"video={camera_index}",  # Kamerka
        "-pix_fmt", "bgr24",  # Format obrazu zgodny z OpenCV
        "-f", "rawvideo",  # Surowy format wideo
        "-"
    ]

    # Uruchomienie FFmpeg w potoku
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, bufsize=10 ** 8)

    # Główna pętla przetwarzająca klatki
    try:
        while True:
            # Odczyt surowej klatki z wyjścia FFmpeg

            raw_frame = process.stdout.read(640 * 480 * 3)  # 640x480 w bgr24 = 3 bajty na piksel
            if not raw_frame:
                pass

            # Konwersja klatki na numpy array
            frame = np.frombuffer(raw_frame, np.uint8).reshape((480, 640, 3))

            # Wyświetlenie klatki (opcjonalne)
            cv2.imshow("Podgląd z kamerki", frame)

            # Przerwij pętlę po naciśnięciu 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        process.terminate()  # Zakończ proces FFmpeg
        cv2.destroyAllWindows()
