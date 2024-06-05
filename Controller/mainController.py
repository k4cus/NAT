from Model.mainModel import mainModel
from View.mainView import mainView


class mainController:
    model = None
    view = None

    def __init__(self):
        self.model = mainModel(self)
        self.view = mainView(self)
        self.model.camera.initialize()

    # def suggestDrink(self, event):
    #     print("KONTROLLER - Kliknieto w przycisk, kaze modelowi wylosowac napoj.")
    #     self.model.suggestDrink()
    #
    # def onDrinkSuggested(self, drink):
    #     print("KONTROLER - Model wylosowal napoj, przekazuje wynik do widoku i aktualizuję widok.")
    #     self.view.tabs[0].setDrink(drink)
    #     self.view.Update()

    def createNewExam(self, e):
        self.model.createNewExam(e.control.data)

    def openExistingExam(self, e):
        self.model.openExistingExam(e.control.data)

    def run(self):
        self.view.run()  # main program loop

    def getExamName(self):
        return self.model.getExamName()

    def getExamsList(self):
        return self.model.getExamsList()

    def onExamOpened(self):
        return self.view.onExamOpened()

    def UpdateView(self):
        self.view.Update()

    def setCameraInputIndex(self, index):
        return self.model.camera.setCameraInputIndex(index)

    def getCameraInputIndex(self):
        return self.model.camera.getCameraInputIndex()

    def getSettings(self):
        return self.model.storage.settings

    def setSetting(self, key, value):
        print("KONTROLLER - Ustawiam ustawienie: " + key + " na wartość: " + str(value))
        settings = self.model.storage.settings
        settings[key] = value
        self.model.storage.settings = settings
