import MySQLdb
from Person import Person


class DataBase:
    db = None
    cursor = None


    # sql = """CREATE TABLE PERSON (
    #      FIRST_NAME  CHAR(20) NOT NULL,
    #      LAST_NAME  CHAR(20),
    #      AGE INT )"""

    def __init__(self):
        self.db = MySQLdb.connect("localhost", "root", "1540487768", "PERSONS")
        self.cursor = self.db.cursor()
        # self.cursor.execute("DROP TABLE IF EXISTS PERSON")
        # self.cursor.execute(self.sql)

    def insert_person(self, person):
        try:
            self.cursor.execute("INSERT INTO PERSON(FIRST_NAME, \
                   LAST_NAME, AGE) \
                   VALUES ('%s', '%s', '%d' )" % \
                   (person.first_name, person.last_name, person.age))
            self.db.commit()
        except:
            print(" except in insert_person method ... ")
            self.db.rollback()

    def show_all_persons(self):
        try:
            self.cursor.execute("SELECT * FROM PERSON")
            results = self.cursor.fetchall()
            for row in results:
                fname = row[0]
                lname = row[1]
                age = row[2]
                print(fname , lname, age)

        except:
            print("Error: unable to fecth data")

    def search(self, person):
        result=[]
        all_data_base = []
        self.cursor.execute("SELECT * FROM PERSON")
        all_data_base = self.cursor.fetchall()

        for row in all_data_base:
            if person.first_name == row[0] or person.last_name == row[1] or person.age == row[2]:
                result.append(Person(row[0], row[1], row[2]))

        return result