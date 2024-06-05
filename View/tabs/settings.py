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
        content = ft.Column(
            [
                languageRow,
            ],
            alignment=ft.MainAxisAlignment.START,
            expand=True
        )
        return content

    def setLanguage(self, e):
        self.mainView.setLanguage(e.control.data)

