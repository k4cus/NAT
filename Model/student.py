class Student:
    _students = {}

    def __init__(self, index, os_id, tested, grade0, name, surname, comment0, comment_student, grade1, comment1, percentage):
        self.index = index  # key
        self.os_id = os_id
        self.tested = tested
        self.grade0 = grade0
        self.name = name  
        self.surname = surname  
        self.comment0 = comment0
        self.comment_student = comment_student
        self.grade1 = grade1
        self.comment1 = comment1
        self.percentage = percentage

    @classmethod
    def add_student(cls, index, os_id="", tested=False, grade0="", name="", surname="", comment0="", comment_student="", grade1="", comment1="", percentage=""):
        if not index in cls._students:
            student = Student(index, os_id, tested, grade0, name, surname, comment0, comment_student, grade1, comment1, percentage)
            cls._students[index] = student
        else:
            cls.modify_student(index, os_id, tested, grade0, name, surname, comment0, comment_student, grade1, comment1, percentage)


    @classmethod
    def get_student(cls, index):
        return cls._students.get(index)
    
    @classmethod
    def delete_student(cls, index):
        if index in cls._students:
            del cls._students[index]
            print(f"Student with index {index} has been deleted.")
        else:
            print(f"Student with index {index} not found.")

    @classmethod
    def modify_student(cls, index, os_id="", tested=False, grade0="", name="", surname="", comment0="", comment_student="", grade1="", comment1="", percentage=""):
        student = cls._students.get(index)
        print("MODIFYING")
        if student:
            if os_id != "":
                student.os_id = os_id
            if tested:
                student.tested = tested
            if grade0 != "":
                student.grade0 = grade0
            if name != "":
                student.name = name
            if surname != "":
                student.surname = surname
            if comment0 != "":
                student.comment0 = comment0
            if comment_student != "":
                student.comment_student = comment_student
            if grade1 != "":
                student.grade1 = grade1
            if comment1 != "":
                student.comment1 = comment1
            if percentage is not "":
                student.percentage = percentage

            print(f"Student with index {index} has been updated.")
        else:
            print(f"Student with index {index} not found.")

    @classmethod
    def get_all_students(cls):
        return [
            [
                student.index, student.os_id, student.tested, student.name, student.surname, 
                student.grade0, student.comment0, student.comment_student, student.grade1, 
                student.comment1, student.percentage
            ]
            for student in cls._students.values()
        ]
