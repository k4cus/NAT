import flet as ft
from flet_core import TextAlign
import i18n

from View.tabs.answers import answersTab
from View.tabs.grayed import grayedTab
from View.tabs.keys import keysTab
from View.tabs.results import resultsTab
from View.tabs.settings import settingsTab
from View.tabs.exam import examTab


class mainView:
    def __init__(self, controller):
        self.controller = controller
        self.page = None
        self.textField = None
        i18n.set('locale', 'pl')
        i18n.set('fallback', 'en')
        i18n.set('file_format', 'json')
        i18n.set('filename_format', '{locale}.{format}')
        i18n.set('skip_locale_root_data', True)
        i18n.load_path.append('lang/')
        self.t = i18n.t

        self.currentlyDisplayedTabIndex = 0
        self.tabs = [
            examTab(controller, self.t),
            keysTab(controller, self.t),
            answersTab(controller, self.t),
            resultsTab(controller, self.t),
            settingsTab(controller, self.t),
            grayedTab(controller, self.t)
        ]
        self.currentlyDisplayedTab = self.tabs[self.currentlyDisplayedTabIndex]

    def run(self):
        ft.app(self.main)

    def main(self, page: ft.Page):
        self.page = page  # widget root
        self.page.vertical_alignment = ft.MainAxisAlignment.CENTER
        self.Update()

    def Update(self):
        print("WIDOK - aktualizuję okno")
        t = self.t
        self.page.title = self.t('title') + " - " + self.controller.getExamName() if self.controller.getExamName() is not None else self.t('title')
        tabContent = self.currentlyDisplayedTab.main() # moved here to prevent visible rendering
        rail = ft.NavigationRail(
            selected_index=self.currentlyDisplayedTabIndex,
            width=100,
            label_type=ft.NavigationRailLabelType.ALL,
            # extended=True,
            # min_width=100,
            # min_extended_width=400,
            # leading=ft.FloatingActionButton(icon=ft.icons.CREATE, text="Add"),
            group_alignment=-0.9,
            destinations=[
                ft.NavigationRailDestination(
                    icon=ft.icons.START,
                    selected_icon=ft.icons.START,
                    label_content=ft.Text(t('menu-exam'), text_align=TextAlign.CENTER),
                ),
                ft.NavigationRailDestination(
                    icon_content=ft.Icon(ft.icons.KEY),
                    selected_icon_content=ft.Icon(ft.icons.KEY),
                    label_content=ft.Text(t('menu-keys'), text_align=TextAlign.CENTER),
                ),
                ft.NavigationRailDestination(
                    icon_content=ft.Icon(ft.icons.QUESTION_ANSWER),
                    selected_icon_content=ft.Icon(ft.icons.QUESTION_ANSWER),
                    label_content=ft.Text(t('menu-answers'), text_align=TextAlign.CENTER),
                ),
                ft.NavigationRailDestination(
                    icon_content=ft.Icon(ft.icons.FACT_CHECK_ROUNDED),
                    selected_icon_content=ft.Icon(ft.icons.FACT_CHECK_ROUNDED),
                    label_content=ft.Text(t("menu-results"), text_align=TextAlign.CENTER),
                ),
                ft.NavigationRailDestination(
                    icon=ft.icons.SETTINGS,
                    selected_icon_content=ft.Icon(ft.icons.SETTINGS),
                    label_content=ft.Text(t('menu-settings'), text_align=TextAlign.CENTER),
                ),
            ],
            on_change=self.onTabChange,
            # expand=True,
        )
        self.page.clean()
        self.page.add(
            ft.Row(
                [
                    rail,
                    ft.VerticalDivider(width=1),
                    tabContent
                ],
                alignment=ft.MainAxisAlignment.START,
                expand=True,
            )
        )
        self.page.update()

    def onTabChange(self, e):
        self.currentlyDisplayedTabIndex = e.control.selected_index
        if (self.currentlyDisplayedTabIndex > 0) and self.controller.getExamName() is None:
            self.currentlyDisplayedTab = self.tabs[5]
        else:
            self.currentlyDisplayedTab = self.tabs[self.currentlyDisplayedTabIndex]
        self.Update()


