class examData:
    def __init__(self, examFolder):
        self.examFolder = examFolder

    def getExamName(self):
        return self.examFolder.split("/")[-2]
