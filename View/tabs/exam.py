import flet as ft
from Model.crypto import verify_password, hash_password, decrypt_folder, derive_key, encrypt_folder, generate_salt
import os
import time


class examTab:
    openedColor = "yellow"
    def __init__(self, controller, t):
        self.t = t
        self.controller = controller
        self.password_input = ft.TextField(password=True, autofocus=True)
        self.dialog = ft.AlertDialog(
            content=ft.Column(
                [
                    ft.Text(t("enter-password")),
                    self.password_input,
                    ft.Row(
                        [
                            ft.ElevatedButton("OK", on_click=self.on_ok),
                        ]
                    ),
                ],
                height = 150
            ),
            modal=True
        )
        self.dialog.open = True

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

        content = (
            ft.Column(
            [
                self.dialog,
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
        ))
        return content

    def on_ok(self, e):
        password = self.password_input.value  # Get password from the input field

        if not os.path.exists("salt.bin"):
            salt = generate_salt()
            with open("salt.bin", "wb") as salt_file:
                salt_file.write(salt)
        else:
            with open("salt.bin", "rb") as salt_file:
                salt = salt_file.read()

        hashed_password = hash_password(password, salt)

        if os.path.exists("hash.bin"):
            no_pass = False
            with open("hash.bin", "rb") as pass_file:
                correct_pass_hash = pass_file.read()
        else:
            no_pass = True
            correct_pass_hash = hashed_password
            with open("hash.bin", "wb") as pass_file:
                pass_file.write(correct_pass_hash)

        key = derive_key(password, salt)

        if correct_pass_hash == hashed_password:
            with open("key.bin", "wb") as key_file:
                key_file.write(key)
            self.dialog.open = False
            self.dialog.update()
            if not no_pass:
                decrypt_folder(key,"exams-data-saved", "exams-data")
            time.sleep(2)
            self.controller.UpdateView()

        else:
            print("Wrong password")
            pass