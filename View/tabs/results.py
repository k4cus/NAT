import flet as ft


class resultsTab:
    def __init__(self, controller, t):
        self.t = t
        self.controller = controller


    def main(self):
        content = ft.Column(
            [

            ],
            alignment=ft.MainAxisAlignment.START,
            expand=True
        )
        return content
