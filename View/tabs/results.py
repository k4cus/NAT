import flet as ft
import os
from Model.usos import import_data

class resultsTab:
    def __init__(self, controller, mainView):
        self.view = mainView
        self.controller = controller
        self.text = "/"
        self.filePicker = ft.FilePicker(on_result=self.onFilePickResult)
        self.filePickerUsos = ft.FilePicker(on_result=self.onFilePickResultUsos)
        self.fileExtensions = self.controller.getReadFromFileExtensions()
        self.ftTextField = ft.TextField(value=self.text, disabled=True)
        self.ftTextFieldImport = ft.TextField(value=self.text, disabled=True)
        self.usosFilePath = ""


    def main(self):
        t = self.view.t
        content = ft.Column(
            [
                self.filePicker,
                self.filePickerUsos,
                ft.Row([
                    ft.Text(t("choose-destination-dir")),
                    self.ftTextField,
                ]),
                ft.Row([
                    ft.Text(t("choose-usos-file")),
                    self.ftTextFieldImport,
                ]),
                ft.Row([
                    ft.ElevatedButton(text=t("pick-directory"), on_click=self.pickDirectoryToRead),
                    ft.ElevatedButton(text=t("pick-usos-file"), on_click=self.pickFileToRead),
                    ft.ElevatedButton(text=t("save-to-dir"), on_click=self.saveToDirectory),
                ]),
                ]
        )
        return content

    def pickDirectoryToRead(self, e):
        self.filePicker.get_directory_path(initial_directory=".")

    def pickFileToRead(self, e):
        self.filePickerUsos.pick_files(allow_multiple=False, allowed_extensions=["csv"], initial_directory=".")

    def onFilePickResult(self, e: ft.FilePickerResultEvent):
        self.text = e.path
        self.ftTextField.value = self.text
        self.ftTextField.update()

    def onFilePickResultUsos(self, e: ft.FilePickerResultEvent):
        self.usosFilePath = e.files[0].path
        self.ftTextFieldImport.value = self.usosFilePath
        self.ftTextFieldImport.update()

    def saveToDirectory(self, e):
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
                        percent = int(p)
                        if percent < 50:
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




