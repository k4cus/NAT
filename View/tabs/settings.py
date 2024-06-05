import flet as ft


class settingsTab:
    def __init__(self, controller, t, mainView):
        self.t = t
        self.controller = controller
        self.mainView = mainView
        self.flag_PL = ft.Image(src="PL.png", width=64, tooltip="Polish")
        self.flag_EN = ft.Image(src="EN.png", width=64, tooltip="English")

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
        content = ft.Column(
            [
                languageRow,
                cameraRow
            ],
            alignment=ft.MainAxisAlignment.START,
            expand=True
        )
        return content

    def setLanguage(self, e):
        self.mainView.setLanguage(e.control.data)

    def setCameraIndex(self, e):
        isInputValid = self.controller.setCameraInputIndex(int(e.control._Control__attrs.get('value')[0]))
        if not isInputValid:
            self.mainView.openAlertDialog('camera-error', 'camera-error-message')


    def getCameraIndex(self):
        return self.controller.getCameraInputIndex()
