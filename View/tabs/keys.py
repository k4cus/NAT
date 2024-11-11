import os

import flet as ft

from Model.utils import base64_empty_image


import cv2
import base64
import io
import threading
import time
from PIL import Image

global fraaaame

class keysTab:
    def __init__(self, controller, mainView):
        self.camera_thread = None
        self.camera_on = False
        self.mainView = mainView
        self.view = mainView
        self.controller = controller
        self.filePicker = ft.FilePicker(on_result=self.onFilePickResult)
        self.fileExtensions = self.controller.getReadFromFileExtensions()
        self.image = base64_empty_image(1240, 1754)
        self.text = ""
        self.ftImage = ft.Image(
            src_base64=self.image,
            height=1754,
            fit=ft.ImageFit.FIT_HEIGHT,
        )
        self.ftText = ft.Text(value=self.text)

    def main(self):
        t = self.view.t
        content = ft.Column(
            [
                self.filePicker,
                ft.Row([
                    # ft.ElevatedButton(text=t("keys-reading-mode"), on_click=self.controller.enterReadingMode,
                    #                   data=["keys", self.controller.getExamName()]),
                    ft.ElevatedButton(text=t("keys-reading-mode"), on_click=self.toggle_camera,
                                                         data=["keys", self.controller.getExamName()]),
                    ft.ElevatedButton(text=t("keys-reading-files"), on_click=self.pickFileToRead),
                    ft.ElevatedButton(text=t("keys-reading-directory"), on_click=self.pickDirectoryToRead)
                ]),
                ft.Row([
                    self.ftImage,
                    self.ftText
                ],
                    expand=1,
                    wrap=False,
                    scroll="always")
            ],
            alignment=ft.MainAxisAlignment.START,
            expand=True
        )
        return content

    def pickDirectoryToRead(self, e):
        self.filePicker.get_directory_path()

    def pickFileToRead(self, e):
        self.filePicker.pick_files(allow_multiple=True, allowed_extensions=self.fileExtensions)

    def onFilePickResult(self, e: ft.FilePickerResultEvent):
        fileList = []
        filePath = []
        if e.path is not None:
            fileList = os.listdir(e.path)
            for file in fileList:
                filePath.append(os.path.join(e.path, file))
        if e.files is not None:
            for file in e.files:
                fileList.append(file.name)
                filePath.append(file.path)
        # filter by file extension
        filePathFiltered = []
        for file in filePath:
            if os.path.splitext(file)[1][1:] in self.fileExtensions:
                filePathFiltered.append(file)
        if len(filePathFiltered) > 0:
            data = ["keys-file", filePathFiltered, self.controller.getExamName()]
            self.controller.enterReadingMode(data)

    def updateImage(self, image):
        self.image = image
        self.ftImage.src_base64 = self.image
        self.ftImage.update()

    def updateText(self, text):
        self.text = text
        self.ftText.value = self.text
        self.ftText.update()

    def toggle_camera(self, e):
        if self.camera_on:
            self.camera_on = False
            e.control.text = "Włącz kamerę"
            self.ftImage.src_base64 = None
            self.ftImage.src = "test.png"
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
                self.controller.enterReadingMode(["keys", self.controller.getExamName()])
        if hasattr(self.mainView, 'page') and self.mainView.page:
            self.mainView.page.update()

    def update_camera_frame(self):
        # self.camera_image.width = 600  # Ustawienie szerokości
        # self.camera_image.height = 400  # Ustawienie wysokośc

        cap = cv2.VideoCapture(0)
        #time.sleep(2)

        while self.camera_on:
            try:
                frame = fraaaame


                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_image = Image.fromarray(frame_rgb)
                buf = io.BytesIO()
                pil_image.save(buf, format="PNG")
                img_bytes = buf.getvalue()

                img_base64 = base64.b64encode(img_bytes).decode("utf-8")

                # if self.camera_image.src == "loading.png":  # Upewnij się, że animacja została załadowana
                #     self.camera_image = ft.Image(width=500, height=320)

                self.ftImage.src_base64 = f"{img_base64}"
                #self.camera_image.src = None

                if hasattr(self.mainView, 'page') and self.mainView.page:
                    self.mainView.page.update()

                time.sleep(1/30)
            except:
                print("F")
            cap.release()
            self.ftImage.src_base64 = None
            # self.camera_image.src = "test.png"

        # if hasattr(self.mainView, 'page') and self.mainView.page:
        #     self.mainView.page.update()

