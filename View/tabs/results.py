import flet as ft


class resultsTab:
    def __init__(self, controller, t):
        self.t = t
        self.controller = controller


    def main(self):
        content = ft.Column(
            [
                ft.Text("Last scanned page:"),
                ft.Image(
                    #src=self.controller.getResultsImg(self.controller.getExamName()),
                    src="page.png",
                    width=490,
                    height=690,
                    fit=ft.ImageFit.CONTAIN,

                ),
                ft.Text("If an image is not displayed, the page was not scanned correctly.")
            ],
            alignment=ft.MainAxisAlignment.START,
            expand=True
        )
        return content
