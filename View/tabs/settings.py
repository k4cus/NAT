import flet as ft
import json

class settingsTab:
    def __init__(self, controller, t, mainView):
        self.t = t
        self.controller = controller
        self.mainView = mainView
        self.flag_PL = ft.Image(src="PL.png", width=64, tooltip="Polish")
        self.flag_EN = ft.Image(src="EN.png", width=64, tooltip="English")
        
        # Base data for grading table
        self.grades_data = controller.getSettings()['grades']

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

        # Create the grading table
        grading_table = self.createGradingTable()

        # Save button
        save_button = ft.ElevatedButton(
            text=self.t("save-grades"),
            on_click=self.saveGrades,
            width=200
        )

        content = ft.Column(
            [
                languageRow,
                cameraRow,
                grading_table,
                save_button
            ],
            alignment=ft.MainAxisAlignment.START,
            expand=True
        )
        return content

    def createGradingTable(self):
        # First row with grades from 3 to 5.5 (read-only input fields)
        grades_row = ft.Row(
            [
                ft.TextField(value="3", disabled=True, border_radius=0, width=100, bgcolor="lightgray", color="black"),
                ft.TextField(value="3.5", disabled=True, border_radius=0, width=100, bgcolor="lightgray", color="black"),
                ft.TextField(value="4", disabled=True, border_radius=0, width=100, bgcolor="lightgray", color="black"),
                ft.TextField(value="4.5", disabled=True, border_radius=0, width=100, bgcolor="lightgray", color="black"),
                ft.TextField(value="5", disabled=True, border_radius=0, width=100, bgcolor="lightgray", color="black"),
                ft.TextField(value="5.5", disabled=True, border_radius=0, width=100, bgcolor="lightgray", color="black"),
            ],
            spacing=0,
            alignment=ft.MainAxisAlignment.START,
            expand=False
        )

        # Second row with input fields for the minimal percentage required for each grade
        input_fields_row = ft.Row(
            [
                ft.TextField(value=str(self.grades_data["3"]), on_change=self.updateGrade, data=3, width=100, border_radius=0),
                ft.TextField(value=str(self.grades_data["3.5"]), on_change=self.updateGrade, data=3.5, width=100, border_radius=0),
                ft.TextField(value=str(self.grades_data["4"]), on_change=self.updateGrade, data=4, width=100, border_radius=0),
                ft.TextField(value=str(self.grades_data["4.5"]), on_change=self.updateGrade, data=4.5, width=100, border_radius=0),
                ft.TextField(value=str(self.grades_data["5"]), on_change=self.updateGrade, data=5, width=100, border_radius=0),
                ft.TextField(value=str(self.grades_data["5.5"]), on_change=self.updateGrade, data=5.5, width=100, border_radius=0),
            ],
            alignment=ft.MainAxisAlignment.START,
            expand=False,
            spacing=0,
        )

        # Combine the rows into a table-like structure
        grading_table = ft.Column(
            [
                grades_row,
                input_fields_row
            ],
            alignment=ft.MainAxisAlignment.START,
            expand=False,
            spacing=0,
        )

        return grading_table

    def updateGrade(self, e):
        # Update the grade value in the dictionary based on user input
        grade = float(e.control.data)
        new_value = e.control.value
        try:
            new_percentage = float(new_value)
            self.grades_data[grade] = new_percentage  # Update the grade data
        except ValueError:
            pass  # Ignore invalid input

    def saveGrades(self, e):
        # Save the grade data to thhe settings file    
        self.controller.setSetting('grades', self.grades_data)


    def setLanguage(self, e):
        self.mainView.setLanguage(e.control.data)

    def setCameraIndex(self, e):
        isInputValid = self.controller.setCameraInputIndex(int(e.control._Control__attrs.get('value')[0]))
        if not isInputValid:
            self.mainView.openAlertDialog('camera-error', 'camera-error-message')

    def getCameraIndex(self):
        return self.controller.getCameraInputIndex()
