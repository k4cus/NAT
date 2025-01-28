import flet as ft
import os
from Model.usos import import_data
from Model.student import Student

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
        self.saveButton = ft.ElevatedButton(text=self.t("save-to-dir"), on_click=self.saveExported, disabled=True)
        self.filePicked = False
        self.resultText = ft.Text(value=self.t("saved-usos"), color="blue", size=20)
        self.dialog = ft.AlertDialog(
            title=ft.Text(self.t("saved-usos-short")),
            content=self.resultText,
            actions=[
                ft.TextButton("OK", on_click=lambda e: self.closeDialog()),
            ],
        )
        self.csv_list = []
        self.updateButton = ft.ElevatedButton(text=self.t("Zaktualizuj"), on_click=self.addGrid, disabled=False)
        self.updateGridButton = ft.ElevatedButton(text=self.t("Zapisz zmiany"), on_click=self.saveGrid, disabled=False)
        
        # Grid components
        self.grid_container = ft.Column(scroll=ft.ScrollMode.AUTO,height=500,spacing=0)

    def main(self):
        t = self.view.t
        content = ft.Column(
            [
                ft.Container(
                    content=ft.Text(value=t("usos-instruction")),
                    padding=ft.padding.only(top=20, bottom=20)
                ),
                ft.Row([
                    ft.ElevatedButton(text=t("pick-usos-file"), on_click=self.pickFileToRead),
                    self.saveButton,
                ]),
                self.filePicker,
                self.filePickerUsos,
                self.dialog,
                ft.Row([
                    ft.Text(t("choose-usos-file")),
                    self.ftTextFieldImport,
                ]),
                ft.Row([
                    self.updateButton,
                    self.updateGridButton
                ]),
                self.grid_container,
            ],
        )
        #self.addGrid()
        return content
    

    def pickDirectoryToRead(self, e):
        self.filePicker.get_directory_path(initial_directory=".")

    def pickFileToRead(self, e):
        self.filePickerUsos.pick_files(allow_multiple=False, allowed_extensions=["csv"], initial_directory=".")

    def unlockSave(self):
        self.saveButton.disabled = False
        self.saveButton.update()

    def onFilePickResult(self, e: ft.FilePickerResultEvent):
        self.text = e.path
        self.dirPicked = True
        self.downloadCSVButton.disabled = False
        self.downloadCSVButton.update()
        self.saveExported()

    def onFilePickResultUsos(self, e: ft.FilePickerResultEvent):
        self.usosFilePath = e.files[0].path
        self.ftTextFieldImport.value = self.usosFilePath
        self.ftTextFieldImport.disabled = False
        self.ftTextFieldImport.update()
        self.filePicked = True
        self.addStudents()
        self.addGrid("")
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
                        line3 = directory + ";" + line2
                        csv_line = []
                        self.csv_list.append(line3.split(";"))
                except:
                    pass
        #self.downloadCSVButton.disabled = False
        #self.downloadCSVButton.update()
        self.addGrid("")

    def saveExported(self, e):
        exam_name = self.controller.getExamName()
        grid_values = []
        # Iterate through each row in the grid container
        for row in self.grid_container.controls:
            row_values = []
            
            # Iterate through each TextField in the row, starting from the 3rd column (index 2)
            for col_index in range(2, len(row.controls)):
                cell = row.controls[col_index]
                
                if isinstance(cell, ft.TextField):  # Ensure it's a TextField
                    row_values.append(cell.value)  # Add the value of the TextField to the row list
            
            grid_values.append(row_values)

        if not os.path.isdir("exams-data/" + exam_name + "/usos/"):
            os.mkdir("exams-data/" + exam_name + "/usos/")
        with open("exams-data/" + exam_name + "/usos/" + "exported.csv", "w") as file:
            for row in grid_values:
                file.write(";".join(row) + "\n")
                    

        
    def saveGrid(self, e):

        grid_values = []
        # Iterate through each row in the grid container
        for row in self.grid_container.controls:
            row_values = []
            
            # Iterate through each TextField in the row, starting from the 3rd column (index 2)
            for col_index in range(0, len(row.controls)):
                cell = row.controls[col_index]
                
                if isinstance(cell, ft.TextField):  # Ensure it's a TextField
                    row_values.append(cell.value)  # Add the value of the TextField to the row list
                else:
                    if cell.src != "empty.png": #[0] - tested
                        row_values.append(True)
                    else:
                        row_values.append(False)
            
            grid_values.append(row_values)

        grid_values = grid_values[1:]
        print(grid_values)
        indexes = []
        for value in grid_values:
            if value[2] != "":
                Student.add_student(index=value[2], os_id=value[3], tested=value[0], grade0=value[6], name=value[4], surname=value[5], 
                                    comment0=value[7], comment_student=value[8], grade1=value[9], comment1=value[10])
                indexes.append(value[2])
        students = Student.get_all_students()

        for student in students:
            if student[0] not in indexes:
                Student.delete_student(student[0])
        self.addGrid("")

        


    def closeDialog(self):
        self.dialog.open = False
        self.dialog.update()

    def addGrid(self, e):
        print("STUDENT")
        students = Student.get_all_students()
        print("STUDENT", students)
        widths = [60, 60, 100, 100, 150, 150, 100, 150, 150, 100, 150]
        print(self.csv_list)
        num_rows = len(students)
        if num_rows <= 0:
            return

        # Clear the grid container
        self.grid_container.controls.clear()

        row0 = ft.Row(
                controls=[
                    ft.TextField(value=f"Test", width=widths[0], disabled=True, border_radius=0),
                    ft.TextField(value=f"USOS", width=widths[1], disabled=True, border_radius=0),
                    ft.TextField(value=f"indeks", width=widths[2], disabled=True, border_radius=0),
                    ft.TextField(value=f"os_id", width=widths[3], disabled=True, border_radius=0),
                    ft.TextField(value=f"imie", width=widths[4], disabled=True, border_radius=0),
                    ft.TextField(value=f"nazwisko", width=widths[5], disabled=True, border_radius=0),
                    ft.TextField(value=f"zerówka", width=widths[6], disabled=True, border_radius=0),
                    ft.TextField(value=f"komentarz", width=widths[7], disabled=True, border_radius=0),
                    ft.TextField(value=f"komentarz dla studenta", width=widths[8], disabled=True, border_radius=0),
                    ft.TextField(value=f"pierwszy termin", width=widths[9], disabled=True, border_radius=0),
                    ft.TextField(value=f"kolejny komentarz", width=widths[10], disabled=True, border_radius=0),
                ],
                spacing=0,
                alignment=ft.MainAxisAlignment.START,
            )

        self.grid_container.controls.append(row0)

        # Create the grid rows and columns
        for row_index in range(num_rows):
            image_src_tested = "answerSheetIcon.png" if students[row_index][2] else "empty.png"
            image_src_usos = "usosIcon.png" if students[row_index][1] else "empty.png"
            students[row_index].pop(2)
            print("BBB", students[row_index])
            row = ft.Row(
                controls=[
                    ft.Container(content=ft.Image(src=image_src_tested), width=60, padding=8),
                    ft.Container(content=ft.Image(src=image_src_usos), width=60, padding=8),
                    *[
                        ft.TextField(value=students[row_index][col], width=widths[col+2], border_radius=0) for col in range(9)
                    ]
                ],
                alignment=ft.MainAxisAlignment.START,
                spacing=0
            )

            for col in range(5):  # Check cells 0-4
                text_field = row.controls[col+2]
                if text_field.value == "":  # If value is missing
                    text_field.bgcolor = "red"  # Set the background color to red
                else:
                    text_field.bgcolor = "white" 

            self.grid_container.controls.append(row)

            self.grid_container.update()
            self.unlockSave()

    def downloadCSV(self, e):
        grid_values = []
        
        # Iterate through each row in the grid container
        for row in self.grid_container.controls:
            row_values = []
            
            # Iterate through each TextField in the row
            for cell in row.controls:
                if isinstance(cell, ft.TextField):
                    row_values.append(cell.value)  # Get the value of each TextField
            
            grid_values.append(row_values)
        
        # Example: Print all the values
        for row in grid_values:
            print(row)

        self.pickDirectoryToRead("")
        
    def addStudents(self):
        os_dict_index = import_data(self.usosFilePath)
        for index in os_dict_index.keys():
            Student.add_student(index, os_id=os_dict_index[index][0], name=os_dict_index[index][1], surname=os_dict_index[index][2])
        print("OS DICT", os_dict_index)
