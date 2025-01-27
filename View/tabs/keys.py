import os
import flet as ft
import cv2
import base64
import numpy as np

from Model.utils import base64_empty_image


class keysTab:
    def __init__(self, controller, mainView):
        self.groups_this_session = []
        self.active_group_index = 0
        self.group_dict = {1: "A", 2: "B", 3: "C", 4: "D"}
        self.group_dict_reverse = {"A": 1, "B": 2, "C": 3, "D": 4}
        self.view = mainView
        self.t = self.view.t
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
            height=690,
            fit=ft.ImageFit.FIT_HEIGHT,
        )
        self.ftText = ft.Text(value=self.text)
        self.ftTextField = ft.TextField(value=self.answers2, on_change=self.updateTextBox, multiline=True, disabled=True)

        self.input_grid = self.create_input_grid()
        self.indexTextField = ft.TextField(label="Indeks", value="", height=30, width=170, max_lines=1, disabled=True, content_padding=2)
        self.groupTextField = ft.TextField(label="Grupa", value="", height=30, width=170, max_lines=1, disabled=True, content_padding=2)

        self.findPageButton = ft.ElevatedButton(text=self.t("manually-find-page"), on_click=self.findPage, disabled=False)
        self.changeAnswersButton = ft.ElevatedButton(text=self.t("change-answers"), on_click=self.changeAnswers, disabled=True)
        self.leftButton = ft.ElevatedButton(text="<", on_click=self.changeImg, data=-1, disabled=True)
        self.rightButton = ft.ElevatedButton(text=">", on_click=self.changeImg, data=1, disabled=True)
        self.dialog = ft.AlertDialog(
            title="",
            content=ft.Text(self.t("manual-page")),
            actions=[
                ft.TextButton("OK", on_click=lambda e: self.closeDialog()),
            ],
        )

    def main(self):
        t = self.t
        content = ft.Column(
            [
                self.filePicker,
                self.dialog,
                ft.Row([
                    ft.ElevatedButton(text=t("keys-reading-mode"), on_click=self.controller.enterReadingMode,
                                      data=["keys", self.controller.getExamName()]),
                    ft.ElevatedButton(text=t("keys-reading-files"), on_click=self.pickFileToRead),
                    ft.ElevatedButton(text=t("keys-reading-directory"), on_click=self.pickDirectoryToRead),
                    self.findPageButton,
                    self.changeAnswersButton
                ]),
                ft.Row([
                    ft.Column([
                        self.ftImage,
                        ft.Row([
                            self.leftButton,
                            self.rightButton,
                            
                        ],
                        alignment = ft.MainAxisAlignment.CENTER,
                        expand=True
                        )
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Column([
                        self.ftText,
                        self.indexTextField,
                        self.groupTextField,
                        self.input_grid
                    ])
                ],
                    expand=1,
                    wrap=False,
                    scroll="always",
                    spacing = 35),
            ],
            alignment=ft.MainAxisAlignment.START,
            expand=True
        )
        return content

    def create_input_grid(self):
        input_fields = []
        for i in range(60):  # Total of 60 fields
            input_field = ft.TextField(label=str(i+1), value="", on_change=self.updateTextBox, height=25, width=50, max_lines=1, disabled=True, content_padding=2)
            input_fields.append(input_field)

        # Organizing input fields into 3 rows of 20 fields each
        cols = []
        for i in range(0, 60, 20):
            col = ft.Column(
                input_fields[i:i+20],  # Selects a slice of 20 fields for each row
                alignment=ft.MainAxisAlignment.START,
                spacing = 7
            )
            cols.append(col)

        # Returning the complete grid structure as a column of rows
        return ft.Row(cols)
        
    def update_input_grid(self, data):
        data = ["" if element == "0" else element for element in data]

        idx = 0  # Index to keep track of position in the data list

        # Iterate over the columns and update each input field
        for column in self.input_grid.controls:
            for input_field in column.controls:
                # Update the value of the corresponding input field
                input_field.value = data[idx]
                input_field.filled = True
                input_field.fill_color = ft.colors.RED_200 if input_field.value == "" else ft.colors.WHITE
                input_field.disabled = False
                idx += 1

        # Update the grid after changing the values
        self.input_grid.update()

    def update_index_group(self, index="", group=""):

        self.indexTextField.value = index
        self.indexTextField.disabled = False
        self.groupTextField.value = self.group_dict[group]
        self.groupTextField.disabled = False
        self.indexTextField.update()
        self.groupTextField.update()

    def changeAnswers(self, e):           
        exam_name = self.controller.getExamName()
        group_number = str(self.group_dict_reverse[self.groupTextField.value])

        answers = []
        for column in self.input_grid.controls:
            for input_field in column.controls:

                answers.append(input_field.value)
                input_field.fill_color = ft.colors.RED_200 if input_field.value == "" else ft.colors.WHITE
        
        self.input_grid.update()


        if not os.path.isdir("exams-data/" + exam_name + "/answer_keys/" + group_number):
            os.mkdir("exams-data/" + exam_name + "/answer_keys/" + group_number)
            image_data = base64.b64decode(self.image)
            nparr = np.frombuffer(image_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            cv2.imwrite("exams-data/" + exam_name + "/answer_keys/" + group_number + "/page_img.png", img)
            self.groups_this_session[self.active_group_index] = group_number
        with open("exams-data/" + exam_name + "/answer_keys/" + str(self.groups_this_session[self.active_group_index]) + "/answers.csv", "w") as f:
            print("Writing")
            f.write(';'.join(answers))

    def updateButton(self):
        self.changeAnswersButton.disabled = False
        self.findPageButton.disabled = False
        self.leftButton.disabled = False
        self.rightButton.disabled = False
        self.changeAnswersButton.update()
        self.findPageButton.update()
        self.rightButton.update()
        self.leftButton.update()

    def changeImg(self, e):
        print("img chamge")
        self.active_group_index += e.control.data
        if self.active_group_index >= len(self.groups_this_session):
            self.active_group_index = 0

        if self.active_group_index < 0:
            self.active_group_index = len(self.groups_this_session) - 1
        print(self.groups_this_session)
        img = cv2.imread("exams-data/" + self.controller.getExamName() + "/answer_keys/" + str(self.groups_this_session[self.active_group_index]) + "/page_img.png")
        #print(img)
        _, buffer = cv2.imencode('.png', img)
        base64_image = base64.b64encode(buffer).decode('utf-8')
        
        self.ftImage.src_base64 = base64_image
        self.ftImage.update()

        with open("exams-data/" + self.controller.getExamName() + "/answer_keys/" + str(self.groups_this_session[self.active_group_index]) + "/answers.csv", "r") as f:
            answers = f.readline().split(";")
        
        self.update_input_grid(answers)
        #print(type(self.groups_this_session[self.active_group_index]))
        self.update_index_group(group=self.groups_this_session[self.active_group_index])

    def addImg(self, group):
        self.groups_this_session.append(group)
        self.active_group_index = len(self.groups_this_session) - 1
        print("add img")

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
        group_dict = {"A": 1, "B": 2, "C": 3, "D": 4}
        if self.answers == self.ftTextField.value:
            pass
        else:
            exam_name = self.controller.getExamName()
            new_answers = self.ftTextField.value.split()
            new_answers_full = [x for x in new_answers if "." not in x]
            new_answers = new_answers_full[2:]
            if new_answers_full[1] not in ["A", "B", "C", "D"]:
                group_number = "0"
            else:
                group_number = str(group_dict[new_answers_full[1]])
            if len(new_answers) == 60:
                new_answers_2 = []
                for i in range(3):
                    for j in range(0, 60, 3):
                        new_answers_2.append(new_answers[i + j])
                if not os.path.isdir("exams-data/" + exam_name + "/answer_keys/" + group_number):
                    os.mkdir("exams-data/" + exam_name + "/answer_keys/" + group_number)
                with open("exams-data/" + exam_name + "/answer_keys/" + group_number + "/answers.csv", "w") as f:
                    print("Writing")
                    f.write(';'.join(new_answers_2))

    def findPage(self, e):
        self.dialog.open = True
        self.dialog.update()
        while self.dialog.open == True:
            print("Waiting")
        print("Go")
        self.controller.keyPageFinder(self.image)

    def generateTemplateAnswers(self, num):
        template = ""
        br = ". "
        for i in range(int(num / 3)):
            if i < 9:
                template += "  "
            template += str(i + 1) + br + str(i + 21) + br + str(i + 41) + br
            template += "\n"
        return template

    def updateAnswers(self, num, answers, index="______", group="0"):
        template = ""
        print(group)
        group_dict = {1: "A", 2: "B", 3: "C", 4: "D"}

        if group == None:
            group_letter = "0"
        elif group in [1, 2, 3, 4]:
            group_letter = group_dict[group]
        else:
            group_letter = "0"
        template += str(index) + "\n" + str(group_letter) + "\n"
        br = ". "
        br2 = "   "
        if answers is not None:
            for i in range(int(len(answers) / 3)):
                if i < 9:
                    template += "  "
                template += str(i + 1) + br + answers[i] + br2 + str(i + 21) + br + answers[i + 20] + br2 + str(i + 41) + br + answers[i + 40]
                template += "\n"

            self.answers2 = template
            self.index = index
            self.group = group
            self.ftTextField.value = self.answers2
            self.ftTextField.disabled = False
            self.ftTextField.update()

    def closeDialog(self):
        self.dialog.open = False
        self.dialog.update()
