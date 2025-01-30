import flet as ft
import os
from Model.usos import import_data
from Model.student import Student
import shutil

class resultsTab:
    def __init__(self, controller, mainView):
        self.view = mainView
        self.t = self.view.t
        self.controller = controller
        self.text = "/"
        self.filePicker = ft.FilePicker(on_result=self.onFilePickResult)
        self.usosExportDirPicker = ft.FilePicker(on_result=self.saveExportedUsos)
        self.exportDirPicker = ft.FilePicker(on_result=self.saveExported)
        self.filePickerUsos = ft.FilePicker(on_result=self.onFilePickResultUsos)
        self.fileExtensions = self.controller.getReadFromFileExtensions()
        self.ftTextField = ft.TextField(value=self.text, disabled=True, width=787)
        self.ftTextFieldImport = ft.TextField(value=self.text, disabled=True, width=700)
        self.usosFilePath = ""
        self.saveButton = ft.ElevatedButton(text=self.t("save-to-dir"), on_click=self.saveExportedDirPicker, disabled=True)
        self.saveButtonUsos = ft.ElevatedButton(text=self.t("save-to-dir-usos"), on_click=self.saveExportedUsosDirPicker, disabled=True)
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
        self.updateButton = ft.ElevatedButton(text=self.t("update-results"), on_click=self.addGrid, disabled=False)
        self.updateGridButton = ft.ElevatedButton(text=self.t("save-results"), on_click=self.saveGrid, disabled=False)
        
        # Grid components
        self.grid_container = ft.Column(scroll=ft.ScrollMode.AUTO,height=500,spacing=0, expand=True,)
        self.grades = controller.getSettings()['grades']

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
                    self.saveButtonUsos
                ]),
                self.filePicker,
                self.usosExportDirPicker,
                self.exportDirPicker,
                self.filePickerUsos,
                self.dialog,
                ft.Row([
                    self.updateButton,
                    self.updateGridButton
                ]),
                self.grid_container,
            ],
        )
        #self.addGrid()
        return content
    

    def saveExportedDirPicker(self, e):
        self.exportDirPicker.get_directory_path(initial_directory=".")

    def saveExportedUsosDirPicker(self, e):
        self.usosExportDirPicker.get_directory_path(initial_directory=".")

    def pickFileToRead(self, e):
        exam_name = self.controller.getExamName()
        if os.path.exists("exams-data/" + exam_name + "/studentListFile.csv"):
            self.onFilePickResultUsos("exams-data/" + exam_name + "/studentListFile.csv")
        else:
            self.filePickerUsos.pick_files(allow_multiple=False, allowed_extensions=["csv"], initial_directory=".")

    def unlockSave(self):
        self.saveButton.disabled = False
        self.saveButton.update()
        self.saveButtonUsos.disabled = False
        self.saveButtonUsos.update()

    def onFilePickResult(self, e: ft.FilePickerResultEvent):
        self.text = e.path
        self.dirPicked = True
        self.saveExported()

    def onFilePickResultUsos(self, e: ft.FilePickerResultEvent):
        exam_name = self.controller.getExamName()
        if isinstance(e, str):
            self.usosFilePath = e
        else:
            if e.files == None:
                return 0
            self.usosFilePath = e.files[0].path
            print(self.usosFilePath)
            shutil.copy(self.usosFilePath, "exams-data/" + exam_name + "/studentListFile.csv")
        self.filePicked = True
        self.addStudents()
        self.addGrid("")
        self.unlockSave()

    def saveExportedUsos(self, e: ft.FilePickerResultEvent):
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
            
            row_values = row_values[1:-1]
            print("AAAA", row_values)
            if row_values[0] != "" and row_values[3] != "":
                grid_values.append(row_values)

        if not os.path.isdir("exams-data/" + exam_name + "/usos/"):
            os.mkdir("exams-data/" + exam_name + "/usos/")
        with open("exams-data/" + exam_name + "/usos/" + "exportedUSOS.csv", "w") as file:
            for row in grid_values:
                file.write(";".join(row) + "\n")
        if e.path != None:
            with open(e.path + "/exportedUSOS.csv", "w") as file:
                for row in grid_values:
                    file.write(";".join(row) + "\n")

    def saveExported(self, e):
        exam_name = self.controller.getExamName()
        grid_values = []

        for row in self.grid_container.controls:
            row_values = []
            
            for col_index in range(2, len(row.controls)):
                cell = row.controls[col_index]
                
                if isinstance(cell, ft.TextField):
                    row_values.append(cell.value)
            
            row_values = [row_values[0], row_values[2], row_values[3], row_values[4], row_values[9]]
            grid_values.append(row_values)

        if not os.path.isdir("exams-data/" + exam_name + "/usos/"):
            os.mkdir("exams-data/" + exam_name + "/usos/")
        with open("exams-data/" + exam_name + "/usos/" + "exported.csv", "w") as file:
            for row in grid_values:
                file.write(";".join(row) + "\n")
        if e.path != None:
            with open(e.path + "/exported.csv", "w") as file:
                for row in grid_values:
                    file.write(";".join(row) + "\n")
                    

        
    def saveGrid(self, e):
        window_width = self.view.page.window_width
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
                    if isinstance(cell.content, ft.Image) and cell.content.src != "empty.png": #[0] - tested
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
        students = Student.get_all_students()
        window_width = self.view.page.window_width - 35

        fixed_widths = [70, 70]  
        fixed_total = sum(fixed_widths)  

        original_widths = [100, 100, 100, 100, 100, 100, 150, 150, 100, 150, 100]  
        total_original_width = sum(original_widths)

        available_width = window_width - fixed_total  

        widths = fixed_widths + [(w / total_original_width) * available_width for w in original_widths]

        num_rows = len(students)
        if num_rows <= 0:
            return

        # Clear the grid container
        self.grid_container.controls.clear()

        row0 = ft.Row(
                controls=[
                    ft.TextField(value=f"Test", width=widths[0], disabled=True, border_radius=0, bgcolor="lightgray", color="black"),
                    ft.TextField(value=f"USOS", width=widths[1], disabled=True, border_radius=0, bgcolor="lightgray", color="black"),
                    ft.TextField(value=f"indeks", width=widths[2], disabled=True, border_radius=0, bgcolor="lightgray", color="black"),
                    ft.TextField(value=f"os_id", width=widths[3], disabled=True, border_radius=0, bgcolor="lightgray", color="black"),
                    ft.TextField(value=f"imie", width=widths[4], disabled=True, border_radius=0, bgcolor="lightgray", color="black"),
                    ft.TextField(value=f"nazwisko", width=widths[5], disabled=True, border_radius=0, bgcolor="lightgray", color="black"),
                    ft.TextField(value=f"zerówka", width=widths[6], disabled=True, border_radius=0, bgcolor="lightgray", color="black"),
                    ft.TextField(value=f"komentarz", width=widths[7], disabled=True, border_radius=0, bgcolor="lightgray", color="black"),
                    ft.TextField(value=f"komentarz dla studenta", width=widths[8], disabled=True, border_radius=0, bgcolor="lightgray", color="black"),
                    ft.TextField(value=f"pierwszy termin", width=widths[9], disabled=True, border_radius=0, bgcolor="lightgray", color="black"),
                    ft.TextField(value=f"kolejny komentarz", width=widths[10], disabled=True, border_radius=0, bgcolor="lightgray", color="black"),
                    ft.TextField(value=f"procent", width=widths[11], disabled=True, border_radius=0, bgcolor="lightgray", color="black"),
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
            row = ft.Row(
                controls=[
                    ft.Container(content=ft.Image(src=image_src_tested), width=70, height=50, padding=8),
                    ft.Container(content=ft.Image(src=image_src_usos), width=70, height=50, padding=8),
                    *[
                        ft.TextField(value=students[row_index][col], width=widths[col+2], border_radius=0, border_color="#aaaaaa") for col in range(10)
                    ]
                ],
                alignment=ft.MainAxisAlignment.START,
                spacing=0,
            )
            print(row.controls[3].value, row.controls[6].value)
            # Check if the 4th (index 3) and 7th (index 6) columns are filled
            if row.controls[3].value != "" and row.controls[6].value != "":
                print(" GREEN")
                # If both columns are filled, set all TextFields to green
                for text_field in row.controls[2:]:
                    text_field.bgcolor = ft.colors.GREEN_50
            else:
                for col in range(5):  # Check cells 0-4
                    text_field = row.controls[col+2]
                    if text_field.value == "":  # If value is missing
                        text_field.bgcolor = ft.colors.RED_50  # Set the background color to red
                    else:
                        text_field.bgcolor = "white" 

            self.grid_container.controls.append(row)

        self.grid_container.update()
        self.unlockSave()


        
    def addStudents(self):
        os_dict_index = import_data(self.usosFilePath)
        for index in os_dict_index.keys():
            Student.add_student(index, os_id=os_dict_index[index][0], name=os_dict_index[index][1], surname=os_dict_index[index][2])
        print("OS DICT", os_dict_index)
