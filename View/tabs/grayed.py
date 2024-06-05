import flet as ft


class grayedTab:
    def __init__(self, controller, t):
        self.t = t
        self.controller = controller
        self.textField = ft.Text(value=t('exam-not-selected'), text_align=ft.TextAlign.CENTER)

    def main(self):
        content = ft.Column(
            [
                self.textField
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True
        )
        return content
