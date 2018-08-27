from DataBase import DataBase
from Person import Person

db = DataBase()
# person = Person("erfan", "erfani", 20)
# db.insert_person(person)
db.show_all_persons()
person = Person("erfa", "fags", 10)
for p in db.search(person):
    print(p.first_name)