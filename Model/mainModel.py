import os
import random
import threading
import time

from Model.config import examsFolder, directories
from Model.examData import examData


class mainModel:

    def __init__(self, controller):
        self.controller = controller
        self.data = None

    # def suggestDrink(self):
    #     print("MODEL - Dostałem polecenie od kontrolera - uruchamiam losowanie w osobnym wątku")
    #     thread = threading.Thread(target=self.lottery)
    #     thread.start()

    # def lottery(self):
    #     print("MODEL - Loteria rozpoczęta")
    #     drink = random.choice(self.drinksList)
    #     time.sleep(2)  # simulate long task
    #     print("MODEL - Loteria zakończona, przekazuje wynik do kontrolera")
    #     self.controller.onDrinkSuggested(drink)

    def createNewExam(self, name):
        print("MODEL - Tworzę nowy folder z egzaminem o nazwie: " + name)
        # create folders
        if not os.path.exists(examsFolder):
            os.makedirs(examsFolder)
        folderCreateDate = time.strftime("%Y-%m-%d_at_%H-%M")
        examFolder = examsFolder + "/" + name + "_on_" + folderCreateDate + "/"

        if os.path.exists(examFolder):
            version = 2
            while os.path.exists(examFolder[:-1] + "_v" + str(version) + "/"):
                version += 1
            examFolder = examFolder[:-1] + "_v" + str(version) + "/"

        os.makedirs(examFolder)
        for folder in directories:
            if not os.path.exists(examFolder + folder):
                os.makedirs(examFolder + folder)

        # store information about which exam is open currently
        self.data = examData(examFolder)
        self.notifyObservers()

    def openExistingExam(self, name):
        print("MODEL - Otwieram folder z egzaminem o nazwie: " + name)
        self.notifyObservers()

    def getExamName(self):
        if self.data is not None:
            return self.data.getExamName()
        return None

    def notifyObservers(self):
        self.controller.UpdateView()
