import os

import flet as ft

from Model.utils import base64_empty_image


class keysTab:
    def __init__(self, controller, mainView):
        self.view = mainView
        self.controller = controller
        self.filePicker = ft.FilePicker(on_result=self.onFilePickResult)
        self.fileExtensions = self.controller.getReadFromFileExtensions()
        self.image = base64_empty_image(1240, 1754)
        self.text = "Test"
        self.answers2 = self.generateTemplateAnswers(60)
        self.answers = self.answers2
        self.ftImage = ft.Image(
            src_base64=self.image,
            height=1754,
            fit=ft.ImageFit.FIT_HEIGHT,
        )
        self.ftText = ft.Text(value=self.text)
        self.ftTextField= ft.TextField(value=self.answers2, on_change=self.updateTextBox, multiline=True, disabled=True,)

    def main(self):
        t = self.view.t
        content = ft.Column(
            [
                self.filePicker,
                ft.Row([
                    ft.ElevatedButton(text=t("keys-reading-mode"), on_click=self.controller.enterReadingMode,
                                      data=["keys", self.controller.getExamName()]),
                    ft.ElevatedButton(text=t("keys-reading-files"), on_click=self.pickFileToRead),
                    ft.ElevatedButton(text=t("keys-reading-directory"), on_click=self.pickDirectoryToRead),
                    ft.ElevatedButton(text=t("manually-find-page"), on_click=self.findPage)
                ]),
                ft.Row([
                    self.ftImage,
                    ft.Column([
                        self.ftText,
                        self.ftTextField  # TODO
                    ])
                ],
                    expand=1,
                    wrap=False,
                    scroll="always"),
                    
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

    def updateTextBox(self, e):
        print("updating...")
        if self.answers == self.ftTextField.value:
            pass
        else:
            exam_name = self.controller.getExamName()
            print(exam_name)
            new_answers = self.ftTextField.value.split()
            new_answers = [ x for x in new_answers if "." not in x ]
            if len(new_answers) == 60:
                new_answers_2 = []
                for i in range(3):
                    print(i)
                    for j in range(0,60,3):
                        print(i+j)
                        new_answers_2.append(new_answers[i+j])
                print(new_answers_2)
                with open("exams-data/" + exam_name + "/answer_keys/answers.csv", "w") as f:
                    f.write(';'.join(new_answers_2) + ";")


    def findPage(self, e):
        self.controller.keyPageFinder(self.image)

    def generateTemplateAnswers(self, num):
        template = ""
        br = ". "
        for i in range(int(num/3)):
            if i < 9:
                template += "  "
            template += str(i+1) + br + str(i+21) + br + str(i+41) + br
            template += "\n"
        return template
    
    def updateAnswers(self, num, answers):
        template = ""
        br = ". "
        br2 = "   "
        for i in range(int(len(answers)/3)):
            if i < 9:
                template += "  "
            template += str(i+1) + br + answers[i] + br2 + str(i+21) + br + answers[i+20] + br2 + str(i+41) + br + answers[i+40]
            template += "\n"
        
        self.answers2 = template
        self.ftTextField.value = self.answers2
        self.ftTextField.disabled = False
        self.ftTextField.update()
        #return template



