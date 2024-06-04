import flet as ft


class examTab:
    def __init__(self, controller, t):
        self.t = t
        self.controller = controller

    def main(self):
        t = self.t
        content = ft.Column(
            [
                ft.Row(
                    [
                        ft.ElevatedButton(text=t("new-exam"), on_click=self.controller.createNewExam, data="nazwa_egzaminu"),
                        ft.ElevatedButton(text=t("open-existing-exam"), on_click=self.controller.openExistingExam, data="nazwa_egzaminu"),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    expand=True
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True
        )
        return content

    def setDrink(self, drink):
        self.textField.value = drink
