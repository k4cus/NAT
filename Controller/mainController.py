from Model.mainModel import mainModel
from View.mainView import mainView


class mainController:
    model = None
    view = None

    def __init__(self):
        self.model = mainModel(self)
        self.view = mainView(self)

    def suggestDrink(self, event):
        print("KONTROLLER - Kliknieto w przycisk, kaze modelowi wylosowac napoj.")
        self.model.suggestDrink()

    def onDrinkSuggested(self, drink):
        print("KONTROLER - Model wylosowal napoj, przekazuje wynik do widoku i aktualizuję widok.")
        self.view.tabs[0].setDrink(drink)
        self.view.Update()

    def run(self):
        self.view.run()  # main program loop
