import asyncio
from balebot.handlers import *
from balebot.filters import *
from balebot.models.messages import *
from balebot.updater import Updater
from Alarm_bot.Alarm import Alarm
import datetime , jdatetime
from Alarm_bot.database_operations import save_alarm

# global variables :

updater =  Updater(token="63d52735b75ff858191152a038d746b956ef950e", loop=asyncio.get_event_loop())
dispatcher = updater.dispatcher
year, month, day, hour, minute = "", "", "", "", ""
invalid_input_message = TextMessage("ورودی اشتباه است ... لطفا دوباره وارد کنید ")



def success(result):
    print("success : ", result)


def failure(result):
    print("failure : ", result)


# Temp Alarm for sending data to databse and save it
alarm = Alarm("", "","","","","",5,False)

# p = PhotoMessage()





def create_time(year, month, day, hour, minute):
    time_string = "{}-{}-{} {}:{}:0.0".format(year, month, day, hour, minute)
    time_string_for_save = "{}:{}:{}:{}:{}".format(year, month, day,hour, minute)
    return time_string_for_save
# Get Start Alarm Information Conversation :

@dispatcher.command_handler(["/create_alarm"])
def start_creating_alarm(bot, update):
    message = TextMessage("سلام و وقت بخیر :) لطفا نام هشدار را وارد نمایید :")
    user_peer = update.get_effective_user()
    alarm.user_id = user_peer.peer_id
    command = update.get_effective_message()
    bot.send_message(message, user_peer, success_callback=success, failure_callback=failure)
    dispatcher.set_conversation_data(update=update, key="alarm_key", value="alarm_value")
    dispatcher.register_conversation_next_step_handler(update, MessageHandler(TextFilter(), get_alarm_name))


def get_alarm_name(bot, update):

    # TODO check that name should not be repetitive .

    message= TextMessage("لطفا پیام هشدار را وارد کنید :")
    user_peer = update.get_effective_user()
    alarm_name = update.get_effective_message()
    alarm.name = alarm_name.text
    # print(alarm_name.text)
    bot.send_message(message, user_peer, success_callback=success, failure_callback=failure)
    dispatcher.set_conversation_data(update=update, key="my_data", value="my_value")
    dispatcher.register_conversation_next_step_handler(update, MessageHandler(TextFilter(), get_alarm_message))


def get_alarm_message(bot, update):
    message = TextMessage("لطفا یک پیام را برای متوقف کردن هشدار ارسال نمایید (یعنی اگر شما آن پیام را ارسال نمایید آن هشدار متوقف خوهاد شد)")
    user_peer = update.get_effective_user()
    alarm_message = update.get_effective_message()
    alarm.message = alarm_message.text
    bot.send_message(message, user_peer, success_callback=success, failure_callback=failure)
    dispatcher.set_conversation_data(update=update, key="my_data", value="my_value")
    dispatcher.register_conversation_next_step_handler(update, MessageHandler(TextFilter(), get_alarm_stop_message))

def get_alarm_stop_message(bot, update):
    message = TextMessage("یک عکس برای هشدار ارسال نمایید :")
    user_peer = update.get_effective_user()
    alarm_stop_message = update.get_effective_message()
    alarm.stop_message = alarm_stop_message.text
    bot.send_message(message, user_peer, success_callback=success, failure_callback=failure)
    dispatcher.set_conversation_data(update=update, key="my_data", value="my_value")
    dispatcher.register_conversation_next_step_handler(update, MessageHandler(PhotoFilter(), get_alarm_photo))


def get_alarm_photo(bot, update):
    # TODO check if message is not a photo message
    message = TextMessage("زمان هشدار : لطفا سال هشدار را وارد نمایید : برای مثال : ‌1397")
    photo = update.get_effective_message()
    alarm.photo = photo.get_json_str()
    user_peer = update.get_effective_user()
    bot.send_message(message, user_peer, success_callback=success, failure_callback=failure)
    dispatcher.set_conversation_data(update=update, key="my_data", value="my_value")
    dispatcher.register_conversation_next_step_handler(update, MessageHandler(TextFilter(), get_date_year))


def get_date_year(bot, update):
    message = TextMessage("لطفا ماه هشدار را وارد نمایید : ")
    global year
    user_peer = update.get_effective_user()
    year = update.get_effective_message().text
    if int(year) < 1397:
        bot.send_message(invalid_input_message, user_peer, success_callback=success, failure_callback=failure)
        dispatcher.register_conversation_next_step_handler(update, MessageHandler(TextFilter(), get_date_year))
    else:
        bot.send_message(message, user_peer, success_callback=success, failure_callback=failure)
        dispatcher.set_conversation_data(update=update, key="my_data", value="my_value")
        dispatcher.register_conversation_next_step_handler(update, MessageHandler(TextFilter(), get_date_month))

def get_date_month(bot, update):
    message = TextMessage("لطفا روز هشدار را وارد نمایید : ")
    global month
    month = update.get_effective_message().text
    user_peer = update.get_effective_user()
    if not (0 < int(month) < 13):
        bot.send_message(invalid_input_message, user_peer, success_callback=success, failure_callback=failure)
        dispatcher.register_conversation_next_step_handler(update, MessageHandler(TextFilter(), get_date_month))
    else:
        bot.send_message(message, user_peer, success_callback=success, failure_callback=failure)
        dispatcher.set_conversation_data(update=update, key="my_data", value="my_value")
        dispatcher.register_conversation_next_step_handler(update, MessageHandler(TextFilter(), get_date_day))


def get_date_day(bot, update):
    message = TextMessage("لطفا ساعت هشدار را وارد نمایید :")
    global day
    day = update.get_effective_message().text
    user_peer = update.get_effective_user()
    if not ((0 < int(day) < 32 and 0 < int(month) < 7) or (0 < int(day) < 31 and 6 < int(month) < 13)) :
        bot.send_message(invalid_input_message, user_peer, success_callback=success, failure_callback=failure)
        dispatcher.register_conversation_next_step_handler(update, MessageHandler(TextFilter(), get_date_day))
    else:
        bot.send_message(message, user_peer, success_callback=success, failure_callback=failure)
        dispatcher.set_conversation_data(update=update, key="my_data", value="my_value")
        dispatcher.register_conversation_next_step_handler(update, MessageHandler(TextFilter(), get_date_hour))


def get_date_hour(bot, update):
    message = TextMessage("لطفا دقیقه هشدار را وارد نمایید :")
    global hour
    hour = update.get_effective_message().text
    user_peer = update.get_effective_user()
    if not 0 <= int(hour) < 24:
        bot.send_message(invalid_input_message, user_peer, success_callback=success, failure_callback=failure)
        dispatcher.register_conversation_next_step_handler(update, MessageHandler(TextFilter(), get_date_hour))
    else:
        bot.send_message(message, user_peer, success_callback=success, failure_callback=failure)
        dispatcher.set_conversation_data(update=update, key="my_data", value="my_value")
        dispatcher.register_conversation_next_step_handler(update, MessageHandler(TextFilter(), get_date_minute))


def get_date_minute(bot, update):
    message = TextMessage("لطفا زمان تکرار هشدار را وارد نمایید (هشدار چند دقیقه یک بار تکرار شود ؟)")
    global minute
    minute = update.get_effective_message().text
    user_peer = update.get_effective_user()
    if not 0 < int(minute) < 60:
        bot.send_message(invalid_input_message, user_peer, success_callback=success, failure_callback=failure)
        dispatcher.register_conversation_next_step_handler(update, MessageHandler(TextFilter(), get_date_minute))
    else:
        # print(create_time(year, month, day, hour, minute))
        alarm.start_time = create_time(year, month, day, hour, minute)
        bot.send_message(message, user_peer, success_callback=success, failure_callback=failure)
        dispatcher.register_conversation_next_step_handler(update, MessageHandler(TextFilter(), finish_creating_alarm))

def finish_creating_alarm(bot, update):
    message = TextMessage("هشدار با موفقیت ساخته شد ... :)")
    user_peer = update.get_effective_user()
    period = update.get_effective_message()
    alarm.repeat_period = period.text
    save_alarm(alarm)
    bot.send_message(message, user_peer, success_callback=success, failure_callback=failure)
    dispatcher.finish_conversation(update)




updater.run()