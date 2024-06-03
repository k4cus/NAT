import flet as ft


class testTab:
    def __init__(self, controller, t):
        self.t = t
        self.controller = controller
        self.textField = ft.TextField(value=t('get-drink'), text_align=ft.TextAlign.CENTER, width=150)

    def main(self):
        content = ft.Column(
            [
                self.textField,
                ft.ElevatedButton(text="Suggest Drink!", on_click=self.controller.suggestDrink),
            ],
            alignment=ft.MainAxisAlignment.START,
            expand=True
        )
        return content

    def setDrink(self, drink):
        self.textField.value = drink
