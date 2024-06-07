import flet as ft


class answersTab:
    def __init__(self, controller, t):
        self.t = t
        self.controller = controller

    def main(self):
        t = self.t
        #print(self.controller.getExamName())
        content = ft.Column(
            [
                ft.ElevatedButton(text=t("answers-reading-mode"), on_click=self.controller.enterReadingMode, data=["answers", self.controller.getExamName()]),

            ],
            alignment=ft.MainAxisAlignment.START,
            expand=True
        )
        return content
