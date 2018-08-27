import asyncio
from balebot.handlers import *
from balebot.filters import *
from balebot.models.messages import *
from balebot.updater import Updater
from PersonInformationBot.Person import Person
from PersonInformationBot.postgres_database import DataBase

# Config.real_time_fetch_updates=True

updater = Updater (token="d821ecf310fde3a4fe485543539c53acebe3c7ae" ,loop=asyncio.get_event_loop())
dispatcher = updater.dispatcher

# create database :
db = DataBase()

# temp person for sending information to database :
person = Person("", "", 0)

command_status = TextMessage
command_status_strig =""

def success(result):
    print("success : ", result)


def failure(result):
    print("failure : ", result)


@dispatcher.command_handler(["/add", "/search"])
def conversation_starter(bot, update):
    message = TextMessage("hi , nice to meet you :)\nplease tell me your name.")
    user_peer = update.get_effective_user()
    global command_status_strig
    global command_status
    command_status = update.get_effective_message()
    command_status_strig = command_status.text
    print(command_status_strig)
    bot.send_message(message, user_peer, success_callback=success, failure_callback=failure)
    dispatcher.set_conversation_data(update=update, key="my_data", value="my_value")
    dispatcher.register_conversation_next_step_handler(update, MessageHandler(TextFilter(), ask_name))


def ask_name(bot, update):
    message = TextMessage("thanks \nplease send me your last name")
    user_peer = update.get_effective_user()
    input_message = update.get_effective_message()
    person.first_name = input_message.text
    bot.send_message(message, user_peer, success_callback=success, failure_callback=failure)
    dispatcher.register_conversation_next_step_handler(update, MessageHandler(TextFilter(), ask_last_name))


def ask_last_name(bot, update):
    message = TextMessage("thanks \nplease send me your age :")
    user_peer = update.get_effective_user()
    input_message = update.get_effective_message()
    person.last_name = input_message.text
    bot.send_message(message, user_peer, success_callback=success, failure_callback=failure)
    dispatcher.register_conversation_next_step_handler(update, MessageHandler(TextFilter(), ask_age))



def ask_age(bot, update):
    message = TextMessage("thanks \ngoodbye ;)")
    user_peer = update.get_effective_user()
    input_message = update.get_effective_message()
    person.age = int(input_message.text)
    bot.send_message(message, user_peer, success_callback=success, failure_callback=failure)
    print(command_status_strig)
    dispatcher.finish_conversation(update)
    print(command_status_strig)
    if command_status_strig == "/add":
        print("command_status is /talk")
        print(person.first_name)
        print(person.last_name)
        print(person.age)
        db.insert_person(person)
    else:
        print("salam")
        show_search_result(bot, update)


def show_search_result(bot, update):
    print("command status is search")
    message = ""
    for p in db.search(person):
        message += "First Name : " + p.first_name + "\nLast Name : " + p.last_name + "\nAge : \n" + str(p.age) + "\n"
    user_peer = update.get_effective_user()
    bot.send_message(TextMessage(message), user_peer, success_callback=success, failure_callback=failure)



updater.run()
