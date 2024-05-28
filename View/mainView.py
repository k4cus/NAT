import flet as ft


class mainView:
    def __init__(self, controller):
        self.controller = controller
        self.page = None
        self.textField = None

    def run(self):
        ft.app(self.main)

    def main(self, page: ft.Page):
        self.page = page  # widget root
        self.page.title = "NAT - PWr grading tool"
        self.page.vertical_alignment = ft.MainAxisAlignment.CENTER

        self.textField = ft.TextField(value="Get Drink", text_align=ft.TextAlign.CENTER, width=150)

        self.page.add(
            ft.Row(
                [ft.Column(
                    [
                        self.textField,
                        ft.ElevatedButton(text="Suggest Drink!", on_click=self.controller.suggestDrink),
                    ],
                )
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            )
        )

    def setDrink(self, drink):
        self.textField.value = drink

    def Update(self):
        print("WIDOK - aktualizuję okno")
        self.page.update()
