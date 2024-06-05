import json

from Model.config import settingsFile


class storage:

    def __init__(self, controller):
        self.controller = controller
        self.__settings = {
            "language": 'pl',
            "cameraIndex": 0,
        }  # defaults

    @property
    def settings(self):
        try:
            with open(settingsFile, 'r') as file:
                self.__settings = json.loads(file.read())
        except FileNotFoundError:
            pass
        except Exception as e:
            print("Error reading settings file", str(e))
        return self.__settings

    @settings.setter
    def settings(self, value):
        self.__settings = value
        file = open(settingsFile, 'w')
        json.dump(self.__settings, file)
        file.close()
