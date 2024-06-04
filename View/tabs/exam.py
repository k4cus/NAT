import flet as ft


class examTab:
    def __init__(self, controller, t):
        self.t = t
        self.controller = controller

    def main(self):
        t = self.t
        examsList = self.controller.getExamsList()
        lv = ft.ListView(expand=1, spacing=10, padding=20, auto_scroll=False, divider_thickness=1)

        def on_hover(e):
            e.control.bgcolor = "blue" if e.data == "true" else None
            e.control.update()

        for exam in examsList:
            lv.controls.append(
                ft.Container(
                    content=ft.Text(t("open") + " " + exam),
                    on_click=self.controller.openExistingExam,
                    on_hover=on_hover,
                    data=exam
                ))

        content = ft.Column(
            [
                ft.Row(
                    [
                        ft.ElevatedButton(text=t("new-exam"), on_click=self.controller.createNewExam, data="nazwa_egzaminu"),
                        # ft.ElevatedButton(text=t("open-existing-exam"), on_click=self.controller.openExistingExam, data="nazwa_egzaminu"),
                    ],
                    # alignment=ft.MainAxisAlignment.CENTER,
                    expand=True
                ),
                ft.Row(
                    [
                        lv,
                    ],
                    alignment=ft.MainAxisAlignment.START,
                    expand=True
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            # horizontal_alignment=ft.CrossAxisAlignment.START,
            expand=True
        )
        return content
