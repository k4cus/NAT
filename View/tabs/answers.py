import flet as ft


class answersTab:
    def __init__(self, controller, t):
        self.t = t
        self.controller = controller
        self.textField = ft.TextField(value='answersTab', text_align=ft.TextAlign.CENTER, width=150)

    def main(self):
        content = ft.Column(
            [
                self.textField,
                ft.ElevatedButton(text="BBBB!", on_click=self.controller.suggestDrink),
            ],
            alignment=ft.MainAxisAlignment.START,
            expand=True
        )
        return content