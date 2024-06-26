import flet as ft


class keysTab:
    def __init__(self, controller, t):
        self.t = t
        self.controller = controller

    def main(self):
        t = self.t
        content = ft.Column(
            [
                ft.ElevatedButton(text=t("keys-reading-mode"), on_click=self.controller.enterReadingMode, data=["keys", self.controller.getExamName()]),
                ft.ElevatedButton(text=t("keys-reading-file"), on_click=self.controller.enterReadingMode, data=["keys-file", self.controller.getExamName()]),
            ],
            alignment=ft.MainAxisAlignment.START,
            expand=True
        )
        return content
