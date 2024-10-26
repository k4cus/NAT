import os

import flet as ft

from Model.utils import base64_empty_image


class answersTab:
    def __init__(self, controller, mainView):
        self.view = mainView
        self.controller = controller
        self.filePicker = ft.FilePicker(on_result=self.onFilePickResult)
        self.fileExtensions = self.controller.getReadFromFileExtensions()
        self.image = base64_empty_image(1240, 1754)
        self.text = "Test"
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
                    ft.ElevatedButton(text=t("answers-reading-mode"), on_click=self.controller.enterReadingMode,
                                      data=["answers", self.controller.getExamName()]),
                    ft.ElevatedButton(text=t("answers-reading-files"), on_click=self.pickFileToRead),
                    ft.ElevatedButton(text=t("answers-reading-directory"), on_click=self.pickDirectoryToRead)
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
            data = ["answers-file", filePathFiltered, self.controller.getExamName()]
            self.controller.enterReadingMode(data)

    def updateImage(self, image):
        self.image = image
        self.ftImage.src_base64 = self.image
        self.ftImage.update()

    def updateText(self, text):
        self.text = text
        self.ftText.value = self.text
        self.ftText.update()

