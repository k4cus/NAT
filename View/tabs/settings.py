import flet as ft
import cv2
import base64
import io
import threading
import time
from PIL import Image

class settingsTab:
    def __init__(self, controller, t, mainView):
        self.t = t
        self.controller = controller
        self.mainView = mainView
        self.flag_PL = ft.Image(src="PL.png", width=64, tooltip="Polish")
        self.flag_EN = ft.Image(src="EN.png", width=64, tooltip="English")
        self.camera_image = ft.Image(src="test.png", width=600, height=400)
        #self.loading_image = ft.Image(src="loading.png", width=600, height=400)
        self.camera_on = False
        self.camera_thread = None
        # threading.Thread(target=self.update_camera_frame, daemon=True).start()

    def main(self):
        languageRow = ft.Row(
            [
                ft.Text(self.t('language')),
                ft.IconButton(
                    content=ft.Row([self.flag_PL], alignment=ft.MainAxisAlignment.SPACE_AROUND),
                    on_click=self.setLanguage,
                    data="pl"
                ),
                ft.IconButton(
                    content=ft.Row([self.flag_EN], alignment=ft.MainAxisAlignment.SPACE_AROUND),
                    on_click=self.setLanguage,
                    data="en"
                ),
            ],
            alignment=ft.MainAxisAlignment.START,
            expand=False
        )

        cameraIndexDropdown = ft.Dropdown(
            on_change=self.setCameraIndex,
            options=[
                ft.dropdown.Option(text=self.t('camera-input') + " 0", key=0),
                ft.dropdown.Option(text=self.t('camera-input') + " 1", key=1),
                ft.dropdown.Option(text=self.t('camera-input') + " 2", key=2),
                ft.dropdown.Option(text=self.t('camera-input') + " 3", key=3),
                ft.dropdown.Option(text=self.t('camera-input') + " DEBUG", key="http://http://192.168.1.108:4747/video"),
            ],
            value=self.getCameraIndex(),
            width=200,
        )
        cameraRow = ft.Row(
            [
                ft.Text(self.t('camera')),
                cameraIndexDropdown,
            ],
            alignment=ft.MainAxisAlignment.START,
            expand=False
        )
        videoRow = ft.Row(
            [self.camera_image],
            alignment=ft.MainAxisAlignment.START,
            expand=False

        )
        toggleButton = ft.ElevatedButton(
            text="Włącz kamerę",
            on_click=self.toggle_camera
        )
        content = ft.Column(
            [
                languageRow,
                cameraRow,
                videoRow,
                toggleButton
            ],
            alignment=ft.MainAxisAlignment.START,
            expand=True
        )
        return content

    def setLanguage(self, e):
        self.mainView.setLanguage(e.control.data)

    def setCameraIndex(self, e):
        isInputValid = self.controller.setCameraInputIndex(int(e.control._Control__attrs.get('value')[0]))
        if not isInputValid:
            self.mainView.openAlertDialog('camera-error', 'camera-error-message')

    def getCameraIndex(self):
        return self.controller.getCameraInputIndex()

    def toggle_camera(self, e):
        if self.camera_on:
            self.camera_on = False
            e.control.text = "Włącz kamerę"
            self.camera_image.src_base64 = None
            self.camera_image.src = "test.png"
            # threading.Thread(target=self.update_camera_frame, daemon=True).start()
            # self.camera_image = ft.Image(src="test.png", width=400, height=300)
            if hasattr(self.mainView, 'page') and self.mainView.page:
                self.mainView.page.update()

            if self.camera_thread is not None:
                self.camera_thread.join()
                self.camera_thread = None
        else:
            self.camera_on = True
            e.control.text = "Wyłącz kamerę"
            # self.camera_image.src_base64 = None
            # self.camera_image = ft.Image(src="test.png", width=400, height=300)
            # threading.Thread(target=self.update_camera_frame, daemon=True).start()
            # self.camera_image = ft.Image(src="test.png", width=400, height=300)
            # self.camera_thread.start()
            # self.camera_image.src = None
            # self.camera_image.src_base64 = None
            #self.camera_image = ft.Image(src="loading.png", width=600, height=400)

            if hasattr(self.mainView, 'page') and self.mainView.page:
                self.mainView.page.update()

            if self.camera_thread is None or not self.camera_thread.is_alive():
                self.camera_thread = threading.Thread(target=self.update_camera_frame, daemon=True)
                self.camera_thread.start()

        if hasattr(self.mainView, 'page') and self.mainView.page:
            self.mainView.page.update()

    def update_camera_frame(self):
        # self.camera_image.width = 600  # Ustawienie szerokości
        # self.camera_image.height = 400  # Ustawienie wysokośc

        cap = cv2.VideoCapture(self.getCameraIndex())
        #time.sleep(2)
        while self.camera_on:
            ret, frame = cap.read()
            if not ret:
                continue

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(frame_rgb)
            buf = io.BytesIO()
            pil_image.save(buf, format="PNG")
            img_bytes = buf.getvalue()

            img_base64 = base64.b64encode(img_bytes).decode("utf-8")

            # if self.camera_image.src == "loading.png":  # Upewnij się, że animacja została załadowana
            #     self.camera_image = ft.Image(width=500, height=320)

            self.camera_image.src_base64 = f"{img_base64}"
            #self.camera_image.src = None

            if hasattr(self.mainView, 'page') and self.mainView.page:
                self.mainView.page.update()

            time.sleep(1/30)

        cap.release()
        self.camera_image.src_base64 = None
        # self.camera_image.src = "test.png"

        # if hasattr(self.mainView, 'page') and self.mainView.page:
        #     self.mainView.page.update()





