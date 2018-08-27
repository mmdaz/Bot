import psycopg2
from Person import Person

class DataBase:
    db = None
    cursor = None

    def __init__(self):
        self.db = psycopg2.connect(database="Bot_Persons", user="matt", password="1540487768", host="127.0.0.1")
        self.cursor = self.db.cursor()

    def create_table(self):
        self.cursor.execute('''CREATE TABLE PERSON 
        (FIRST_NAME     CHAR(10)       NOT NULL ,
        LAST_NAME       CHAR(15),
        AGE             INT            NOT NULL 
        );''')
        self.db.commit()

    def insert_person(self, person):
        self.cursor.execute("INSERT INTO PERSON(FIRST_NAME, \
                   LAST_NAME, AGE) \
                   VALUES ('%s', '%s', '%d' )" % \
                   (person.first_name, person.last_name, person.age))
        self.db.commit()

    def show_all_database(self):
        self.cursor.execute("SELECT * from PERSON")
        rows = self.cursor.fetchall()

        for row in rows:
            print("FIRST NAME :", row[0])
            print("LAST NAME : ", row[1])
            print("AGE :", row[2])

    def search(self, person):
        result=[]
        all_data_base = []
        self.cursor.execute("SELECT * FROM PERSON")
        all_data_base = self.cursor.fetchall()

        for row in all_data_base:
            if person.first_name == row[0] or person.last_name == row[1] or person.age == row[2]:
                result.append(Person(row[0], row[1], row[2]))

        return result