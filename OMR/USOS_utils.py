import csv

# 0. needs a list of nr_albumu, points and grading system
# 1. export data from USOS (input a file)
# 2. choose an exam type ("zerówka" or "pierwszy termin")
# 3. from the inputted file take [os_id, imie, nazwisko] - can be found by nr_albumu
# 4. generate a file to import

grades = {
    "2": 0,
    "3": 50,
    "3.5": 60,  # TODO check if . or ,
    "4": 70,
    "4.5": 80,
    "5": 90,
    "5.5": 100
}

exam_type = 0  # TODO check how many times can you take an exam

data = []

example_results = {
    "261269": 73,
    "231346": 44
}

results = example_results

with open("../data/exportFromUSOS.csv") as csv_file:
    imported_USOS_file = csv.reader(csv_file, delimiter=";")

    line_count = 0
    for row in imported_USOS_file:
        if line_count == 0:
            print(f'Column names are {", ".join(row)}')
            line_count += 1
        else:
            data.append([row[0], row[1], row[3], row[4]])
            line_count += 1

print(data)

export_csv = ""
# os_id;imie;nazwisko;zerówka;komentarz;komentarz dla studenta;pierwszy termin;kolejny komentarz
for student in data:
    if student[1] in results.keys():
        # print("match")
        line = ';'.join([student[0], student[2], student[3], "", "", "", "", ""])  # TODO add more
    export_csv += (line + "\n")

print(export_csv)

with open("../data/test_results.csv", "w") as csv_file:
    csv_file.write(export_csv)