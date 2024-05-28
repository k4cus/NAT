import random
import threading
import time


class mainModel:
    drinksList = ["Ice coffee", "Hot coffee", "Peach Tymbark", "Orange juice", "Ice Tea", "Hot tea", "Banana smoothie"]

    def __init__(self, controller):
        self.controller = controller
        pass

    def suggestDrink(self):
        print("MODEL - Dostałem polecenie od kontrolera - uruchamiam losowanie w osobnym wątku")
        thread = threading.Thread(target=self.lottery)
        thread.start()

    def lottery(self):
        print("MODEL - Loteria rozpoczęta")
        drink = random.choice(self.drinksList)
        time.sleep(2)  # simulate long task
        print("MODEL - Loteria zakończona, przekazuje wynik do kontrolera")
        self.controller.onDrinkSuggested(drink)
