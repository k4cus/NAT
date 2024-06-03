import flet as ft


class keysTab:
    def __init__(self, controller, t):
        self.t = t
        self.controller = controller
        self.textField = ft.TextField(value='keyTab', text_align=ft.TextAlign.CENTER, width=150)

    def main(self):
        content = ft.Column(
            [
                self.textField,
                ft.ElevatedButton(text="AAA!", on_click=self.controller.suggestDrink),
            ],
            alignment=ft.MainAxisAlignment.START,
            expand=True
        )
        return content
