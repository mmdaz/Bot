import asyncio
from balebot.handlers import *
from balebot.filters import *
from balebot.models.base_models import Peer
from balebot.models.messages import *
from balebot.updater import Updater
from balebot.config import Config
from Person import Person
from DataBase import DataBase

# Config.real_time_fetch_updates=True

updater = Updater (token="d821ecf310fde3a4fe485543539c53acebe3c7ae" ,loop=asyncio.get_event_loop())
dispatcher = updater.dispatcher

db = DataBase()

ms = TextMessage("salam")
print(ms.text)
person = Person("", "", 0)



def success(result):
    print("success : ", result)


def failure(result):
    print("failure : ", result)


@dispatcher.command_handler(["talk"])
def conversation_starter(bot, update):
    message = TextMessage("hi , nice to meet you :)\nplease tell me your name.")
    user_peer = update.get_effective_user()
    bot.send_message(message, user_peer, success_callback=success, failure_callback=failure)
    dispatcher.set_conversation_data(update=update, key="my_data", value="my_value")
    dispatcher.register_conversation_next_step_handler(update, MessageHandler(TextFilter(), ask_name))


@dispatcher.message_handler(filters=TextFilter())
@dispatcher.command_handler(["talk"])
def ask_name(bot, update):
    message = TextMessage("thanks \nplease send me your last name")
    user_peer = update.get_effective_user()
    input_message = update.get_effective_message()
    person.first_name = input_message.text
    bot.send_message(message, user_peer, success_callback=success, failure_callback=failure)
    dispatcher.register_conversation_next_step_handler(update, MessageHandler(TextFilter(), ask_last_name))


@dispatcher.message_handler(filters=TextFilter())
@dispatcher.command_handler(["talk"])
def ask_last_name(bot, update):
    message = TextMessage("thanks \nplease send me your age :")
    user_peer = update.get_effective_user()
    input_message = update.get_effective_message()
    person.last_name = input_message.text
    bot.send_message(message, user_peer, success_callback=success, failure_callback=failure)
    dispatcher.register_conversation_next_step_handler(update, MessageHandler(TextFilter(), ask_age))


@dispatcher.message_handler(filters=TextFilter())
@dispatcher.command_handler(["talk"])
def ask_age(bot, update):
    message = TextMessage("thanks \ngoodbye ;)")
    user_peer = update.get_effective_user()
    input_message = update.get_effective_message()
    person.age = int(input_message.text)
    bot.send_message(message, user_peer, success_callback=success, failure_callback=failure)
    dispatcher.finish_conversation(update)
    print(person.first_name)
    print(person.last_name)
    print(person.age)
    db.insert_person(person)


# @dispatcher.command_handler(["search"])
# def search_conversation_start(bot, update):
#     message = TextMessage("hi , nice to meet you :)\nplease tell me your first name : ")
#     user_peer = update.get_effective_user()
#     bot.send_message(message, user_peer, success_callback=success, failure_callback=failure)
#     dispatcher.set_conversation_data(update=update, key="my_data", value="my_value")
#     dispatcher.register_conversation_next_step_handler(update, MessageHandler(TextFilter(), ask_name))
#

updater.run()
