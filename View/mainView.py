import flet as ft
from flet_core import TextAlign
import i18n

class mainView:
    def __init__(self, controller):
        self.controller = controller
        self.page = None
        self.textField = None
        self.currentlyDisplayedTab = 0
        i18n.set('locale', 'pl')
        i18n.set('fallback', 'en')
        i18n.set('file_format', 'json')
        i18n.load_path.append('../lang/')
        self.t = i18n.t

    def run(self):
        ft.app(self.main)

    def main(self, page: ft.Page):
        self.page = page  # widget root
        self.page.title = "NAT - PWr grading tool"
        self.page.vertical_alignment = ft.MainAxisAlignment.CENTER

        self.textField = ft.TextField(value=self.t('get-drink'), text_align=ft.TextAlign.CENTER, width=150)

        rail = ft.NavigationRail(
            selected_index=self.currentlyDisplayedTab,
            width=100,
            label_type=ft.NavigationRailLabelType.ALL,
            # extended=True,
            # min_width=100,
            # min_extended_width=400,
            # leading=ft.FloatingActionButton(icon=ft.icons.CREATE, text="Add"),
            group_alignment=-0.9,
            destinations=[
                ft.NavigationRailDestination(
                    icon=ft.icons.ADD_CARD,
                    selected_icon=ft.icons.ADD,
                    label_content=ft.Text("Test", text_align=TextAlign.CENTER),
                ),
                ft.NavigationRailDestination(
                    icon_content=ft.Icon(ft.icons.BOOKMARK_BORDER),
                    selected_icon_content=ft.Icon(ft.icons.BOOKMARK),
                    label_content=ft.Text("Klucze odpowiedzi", text_align=TextAlign.CENTER),
                ),
                ft.NavigationRailDestination(
                    icon_content=ft.Icon(ft.icons.BOOKMARK_BORDER),
                    selected_icon_content=ft.Icon(ft.icons.BOOKMARK),
                    label_content=ft.Text("Odpowiedzi studentow", text_align=TextAlign.CENTER),
                ),
                ft.NavigationRailDestination(
                    icon_content=ft.Icon(ft.icons.BOOKMARK_BORDER),
                    selected_icon_content=ft.Icon(ft.icons.BOOKMARK),
                    label_content=ft.Text("Wyniki", text_align=TextAlign.CENTER),
                ),
                ft.NavigationRailDestination(
                    icon=ft.icons.SETTINGS_OUTLINED,
                    selected_icon_content=ft.Icon(ft.icons.SETTINGS),
                    label_content=ft.Text("Ustawienia", text_align=TextAlign.CENTER),
                ),
            ],
            on_change=self.onTabChange,
            # expand=True,
        )

        self.page.add(
            ft.Row(
                [
                    rail,
                    ft.VerticalDivider(width=1),
                    ft.Column(
                    [
                            self.textField,
                            ft.ElevatedButton(text="Suggest Drink!", on_click=self.controller.suggestDrink),
                            ],
                            alignment=ft.MainAxisAlignment.START,
                            expand=True
                    )
                ],
                alignment=ft.MainAxisAlignment.START,
                expand=True,
            )
        )

    def onTabChange(self, e):
        self.currentlyDisplayedTab = e.control.selected_index
        print("Current tab: ", self.currentlyDisplayedTab)

    def setDrink(self, drink):
        self.textField.value = drink

    def Update(self):
        print("WIDOK - aktualizuję okno")
        self.page.update()
