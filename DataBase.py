import MySQLdb

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

    def insert_person(self, firs_name, last_name, age):
        try:
            self.cursor.execute("INSERT INTO PERSON(FIRST_NAME, \
                   LAST_NAME, AGE) \
                   VALUES ('%s', '%s', '%d' )" % \
                   (firs_name, last_name, age))
            self.db.commit()
        except:
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



