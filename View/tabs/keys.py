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
        self.text = ""
        self.index = "123456"
        self.group = "0"
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
        self.filePicker.get_directory_path(initial_directory=".")

    def pickFileToRead(self, e):
        self.filePicker.pick_files(allow_multiple=True, allowed_extensions=self.fileExtensions, initial_directory=".")

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
        group_dict = {"A": 1, "B": 2, "C" : 3, "D": 4}
        if self.answers == self.ftTextField.value:
            pass
        else:
            exam_name = self.controller.getExamName()
            new_answers = self.ftTextField.value.split()
            new_answers_full = [ x for x in new_answers if "." not in x ]
            new_answers = new_answers_full[2:]
            if new_answers_full[1] not in ["A", "B", "C", "D"]:
                group_number = "0"
            else:
                group_number = str(group_dict[new_answers_full[1]])
            if len(new_answers) == 60:
                new_answers_2 = []
                for i in range(3):
                    for j in range(0,60,3):
                        new_answers_2.append(new_answers[i+j])
                if not os.path.isdir("exams-data/" + exam_name + "/answer_keys/" + group_number):
                    os.mkdir("exams-data/" + exam_name + "/answer_keys/" + group_number)
                with open("exams-data/" + exam_name + "/answer_keys/" + group_number + "/answers.csv", "w") as f:
                    print("Writing")
                    f.write(';'.join(new_answers_2))


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
    
    def updateAnswers(self, num, answers, index="______", group="0"):
        template = ""
        print(group)
        group_dict = {1: "A", 2: "B", 3: "C", 4: "D"}

        if group == None:
            group_letter = "0"        
        elif group in [1,2,3,4]:
            group_letter = group_dict[group]
        else:
            group_letter = "0"
        template += str(index) + "\n" + str(group_letter) + "\n"
        br = ". "
        br2 = "   "
        if answers is not None:
            for i in range(int(len(answers)/3)):
                if i < 9:
                    template += "  "
                template += str(i+1) + br + answers[i] + br2 + str(i+21) + br + answers[i+20] + br2 + str(i+41) + br + answers[i+40]
                template += "\n"
        
            self.answers2 = template
            self.index = index
            self.group = group
            self.ftTextField.value = self.answers2
            self.ftTextField.disabled = False
            self.ftTextField.update()
        #return template



