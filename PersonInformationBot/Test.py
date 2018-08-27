from PersonInformationBot.postgres_database import DataBase
from PersonInformationBot.Person import Person

# db = DataBase()
# # person = Person("erfan", "erfani", 20)
# # db.insert_person(person)
# db.show_all_persons()
# person = Person("erfa", "fags", 10)
# for p in db.search(person):
#     print(p.first_name)

p = Person('muhammad', 'azhdari', 20)
db = DataBase()
# db.insert_person(p)
db.show_all_database()
for p in db.search(Person("muhammad", "azhdari", 20 )):
    print(p.first_name)