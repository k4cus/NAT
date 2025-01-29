from Controller.mainController import mainController

if __name__ == "__main__":
    controller = mainController()
    controller.run()
    controller.cleanTempData()
