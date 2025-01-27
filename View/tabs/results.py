import flet as ft
import os
from Model.usos import import_data

class resultsTab:
    def __init__(self, controller, mainView):
        self.view = mainView
        self.t = self.view.t
        self.controller = controller
        self.text = "/"
        self.filePicker = ft.FilePicker(on_result=self.onFilePickResult)
        self.filePickerUsos = ft.FilePicker(on_result=self.onFilePickResultUsos)
        self.fileExtensions = self.controller.getReadFromFileExtensions()
        self.ftTextField = ft.TextField(value=self.text, disabled=True, width=787)
        self.ftTextFieldImport = ft.TextField(value=self.text, disabled=True, width=700)
        self.usosFilePath = ""
        self.saveButton = ft.ElevatedButton(text=self.t("save-to-dir"), on_click=self.saveToDirectory, disabled=True)
        self.filePicked = False
        self.dirPicked = False
        self.resultText = ft.Text(value=self.t("saved-usos"), color="blue", size=20)
        self.dialog = ft.AlertDialog(
            title=ft.Text(self.t("saved-usos-short")),
            content=self.resultText,
            actions=[
                ft.TextButton("OK", on_click=lambda e: self.closeDialog()),
            ],
        )


    def main(self):
        t = self.view.t
        content = ft.Column(
            [
                ft.Container(
                    content=ft.Text(value=t("usos-instruction")),
                    padding=ft.padding.only(top=20, bottom=20)
                ),
                ft.Row([
                    ft.ElevatedButton(text=t("pick-directory"), on_click=self.pickDirectoryToRead),
                    ft.ElevatedButton(text=t("pick-usos-file"), on_click=self.pickFileToRead),
                    self.saveButton,
                ]),
                self.filePicker,
                self.filePickerUsos,
                self.dialog,
                ft.Row([
                    ft.Text(t("choose-destination-dir")),
                    self.ftTextField,
                ]),
                ft.Row([
                    ft.Text(t("choose-usos-file")),
                    self.ftTextFieldImport,
                ]),
                ]
        )
        return content

    def pickDirectoryToRead(self, e):
        self.filePicker.get_directory_path(initial_directory=".")

    def pickFileToRead(self, e):
        self.filePickerUsos.pick_files(allow_multiple=False, allowed_extensions=["csv"], initial_directory=".")

    def unlockSave(self):
        if self.dirPicked == True and self.filePicked == True:
            self.saveButton.disabled = False
            self.saveButton.update()

    def onFilePickResult(self, e: ft.FilePickerResultEvent):
        self.text = e.path
        self.ftTextField.value = self.text
        self.ftTextField.disabled = False
        self.ftTextField.update()
        self.dirPicked = True
        self.unlockSave()

    def onFilePickResultUsos(self, e: ft.FilePickerResultEvent):
        self.usosFilePath = e.files[0].path
        self.ftTextFieldImport.value = self.usosFilePath
        self.ftTextFieldImport.disabled = False
        self.ftTextFieldImport.update()
        self.filePicked = True
        self.unlockSave()

    def saveToDirectory(self, e):
        t = self.view.t
        os_dict_index = import_data(self.usosFilePath)
        exam_name = self.controller.getExamName()

        base_directory = os.path.join(os.getcwd(), "exams-data", exam_name, "student_answers")
        csv_list = []
        csv_list.append("os_id;imie;nazwisko;zerówka;komentarz;komentarz dla studenta;pierwszy termin;kolejny komentarz")
        for root, dirs, files in os.walk(base_directory):
            for directory in dirs:
                try:
                    os_dict = os_dict_index[directory]
                    os_id = os_dict[0]
                    with open(os.path.join(root, directory, "answers.csv")) as f:
                        line = f.readline().split(";")
                        p = line[3][:-3]
                        try:
                            percent = int(p)
                        except:
                            percent = -1
                        if percent == -1:
                            grade = ""
                        elif percent < 50:
                            grade = 2
                        elif percent < 60:
                            grade = 3
                        elif percent < 70:
                            grade = 3.5
                        elif percent < 80:
                            grade = 4
                        elif percent < 90:
                            grade = 4.5
                        elif percent < 100:
                            grade = 5
                        else:
                            grade = 5.5
                        line2 = str(os_id) + ";" + os_dict[1] + ";" + os_dict[2] + ";" + str(grade) + ";;;;;"
                        csv_list.append(line2)
                except:
                    pass
        filename = exam_name + "_answers.csv"
        with open(os.path.join(self.text, filename), "w") as f:
            for file in csv_list:
                f.write(file + "\n")
        
        self.result = t("saved-text")
        self.resultText.value = self.result
        self.resultText.update()
        self.dialog.open = True
        self.dialog.update()

    def closeDialog(self):
        self.dialog.open = False
        self.dialog.update()
