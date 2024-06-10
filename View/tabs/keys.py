import flet as ft


class keysTab:
    def __init__(self, controller, mainView):
        self.view = mainView
        self.controller = controller
        self.filePicker = ft.FilePicker(on_result=self.onFilePickResult)

    def main(self):
        t = self.view.t
        content = ft.Column(
            [
                self.filePicker,
                ft.ElevatedButton(text=t("keys-reading-mode"), on_click=self.controller.enterReadingMode,
                                  data=["keys", self.controller.getExamName()]),
                ft.ElevatedButton(text=t("keys-reading-files"), on_click=self.pickFileToRead),
                ft.ElevatedButton(text=t("keys-reading-directory"), on_click=self.pickDirectoryToRead)
            ],
            alignment=ft.MainAxisAlignment.START,
            expand=True
        )
        return content

    def pickDirectoryToRead(self, e):
        self.filePicker.get_directory_path()

    def pickFileToRead(self, e):
        self.filePicker.pick_files(allow_multiple=True, allowed_extensions=["pdf", "png", "jpg"])
        # self.controller.enterReadingMode("keys-file", self.view.filePicker.result)

    def onFilePickResult(self, e: ft.FilePickerResultEvent):
        print("on file pick path: ", e.path)
        print("on file pick files: ", e.files)
