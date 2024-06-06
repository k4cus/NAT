import flet as ft


class answersTab:
    def __init__(self, controller, t):
        self.t = t
        self.controller = controller

    def main(self):
        t = self.t
        content = ft.Column(
            [
                ft.ElevatedButton(text=t("answers-reading-mode"), on_click=self.controller.enterReadingMode, data="answers"),
            ],
            alignment=ft.MainAxisAlignment.START,
            expand=True
        )
        return content
