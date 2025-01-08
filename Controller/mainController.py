import base64

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

    def enterReadingMode(self, e):
        print(e)
        if hasattr(e, 'control'):
            data = e.control.data
        else:
            data = e
        if data[0] == "keys":
            self.model.enterKeysReadingMode(data[1])
        elif data[0] == "answers":
            self.model.enterAnswersReadingMode(data[1])
        elif data[0] == "keys-file":
            img, score, answers, group, index = self.model.readKeysFromFile(data[1], data[2])
            self.keyUpdateImage(img)
            self.keyUpdateText(index, score, answers, group)
        elif data[0] == "answers-file":
            img, score, answers, group, index = self.model.readAnswersFromFile(data[1], data[2])
            self.answerUpdateImage(img)
            self.answerUpdateText(score, answers, index, group)
        else:
            print("KONTROLLER - enterReadingMode unknown data: " + data[0])

    def getResultsImg(self, exam_name):
        print("img path")
        print(exam_name)
        return self.model.getResultsImgPath(exam_name)

    def getReadFromFileExtensions(self):
        return self.model.readFromFileExtensions

    def keyUpdateImage(self, image):
        img_base64 = self.model.omr.imageToBase64(image)
        self.view.tabs[1].updateImage(img_base64)

    def answerUpdateImage(self, image):
        img_base64 = self.model.omr.imageToBase64(image)
        self.view.tabs[2].updateImage(img_base64)

    def keyUpdateText(self,index, text, answers, group):
        txt = text
        self.view.tabs[1].updateText(txt)
        grupy=["A", "B", "C", "D"]
        self.view.tabs[1].updateAnswers(num=60, answers=answers, group=grupy[int(group)-1], )

    def answerUpdateText(self, text, answers, index, group):
        txt = text
        self.view.tabs[2].updateText(txt)
        grupy = ["A", "B", "C", "D"]
        self.view.tabs[2].updateAnswers(num=60, answers=answers, index=index, group=grupy[int(group)-1])
        
    def keyPageFinder(self, image):
        self.keyUpdateImage(self.model.pageFinder(image))

    def answerPageFinder(self, image):
        self.answerUpdateImage(self.model.pageFinder(image))