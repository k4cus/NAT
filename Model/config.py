from aenum import StrEnum

examsFolder = 'exams-data'
settingsFile = 'settings.json'

class directories(StrEnum):
    KEYS = 'answer_keys'
    ANSWERS = 'student_answers'
