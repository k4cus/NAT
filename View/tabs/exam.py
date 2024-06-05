import flet as ft


class examTab:
    openedColor = "yellow"
    def __init__(self, controller, t):
        self.t = t
        self.controller = controller

    def main(self):
        t = self.t
        examsList = self.controller.getExamsList()
        lv = ft.ListView(expand=1, spacing=10, padding=20, auto_scroll=False, divider_thickness=1)

        def on_hover(e):
            e.control.bgcolor = "blue" if e.data == "true" else self.openedColor if self.controller.getExamName() == e.control.data else None
            e.control.update()

        for exam in examsList:
            lv.controls.append(
                ft.Container(
                    content=ft.Text(t("opened") + " " + exam if self.controller.getExamName() == exam else t("open") + " " + exam,
                                    weight=ft.FontWeight.BOLD if self.controller.getExamName() == exam else None),
                    on_click=self.controller.openExistingExam,
                    on_hover=on_hover,
                    bgcolor=self.openedColor if self.controller.getExamName() == exam else None,
                    data=exam
                ))

        content = ft.Column(
            [
                ft.Row(
                    [
                        ft.Column(
                            [
                                ft.Row(
                                    [
                                        ft.Text("Lista egzaminów:", theme_style=ft.TextThemeStyle.TITLE_SMALL),
                                        ft.ElevatedButton(text=t("new-exam"), on_click=self.controller.createNewExam, data="nazwa_egzaminu"),
                                    ],
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    expand=False
                                ),
                                lv
                            ],
                            alignment=ft.MainAxisAlignment.START,
                            expand=True
                        )
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    expand=True
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            # horizontal_alignment=ft.CrossAxisAlignment.START,
            expand=True
        )
        return content
