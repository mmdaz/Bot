import asyncio

from balebot.filters import TextFilter, PhotoFilter
from balebot.handlers import MessageHandler
from balebot.models.messages import TextMessage, PhotoMessage, PurchaseMessage
from balebot.models.messages.banking.money_request_type import MoneyRequestType
from balebot.updater import Updater
from Alarm_bot.alarm import Alarm
from Alarm_bot.debt import Debt
from Alarm_bot.template_messages import Message
from balebot.models.base_models import Peer
import jdatetime
from Alarm_bot.database_operations import save_alarm, search_alarm_for_send, update_alarm_time, search_stop_message, \
    update_alarm_activation, check_stop_message_repetition, save_debt, search_debt_for_send, save_photo, get_photo_id , get_photo_by_id

# global variables :

loop = asyncio.get_event_loop()
updater =  Updater(token="63d52735b75ff858191152a038d746b956ef950e", loop=loop)
dispatcher = updater.dispatcher




def success(result):
    print("success : ", result)


def failure(result):
    print("failure : ", result)



async def send_alarm(bot = dispatcher.bot):
    while(True):
        current_time = jdatetime.datetime.now()
        if current_time.hour == 17:
            for debt in search_debt_for_send(current_time):
                user_peer = Peer.load_from_json(debt.user_id)
                target_photo = get_photo_by_id(debt.photo_id)
                photo_message = PhotoMessage(target_photo.file_id, target_photo.access_hash, target_photo.name, target_photo.file_size, target_photo.mime_type, target_photo.thumb, target_photo.width, target_photo.height, target_photo.ext_width, target_photo.ext_height, target_photo.file_storage_version,
                                              TextMessage(target_photo.caption_text), target_photo.checksum, target_photo.algorithm)
                photo_message.caption_text = TextMessage(debt.creditor_name)
                purchase_message = PurchaseMessage(photo_message, debt.card_number, debt.amount, MoneyRequestType.normal )
                bot.send_message(purchase_message, user_peer, success_callback=success, failure_callback=failure)
        for alarm in search_alarm_for_send(current_time):
            user_peer = Peer.load_from_json(alarm.user_id)
            update_alarm_time(alarm)
            photo = PhotoMessage.load_from_json(alarm.photo_json)
            # TODO add caption to photo :|||
            photo.caption_text = TextMessage(alarm.message)
            bot.send_message(photo, user_peer, success_callback=success, failure_callback=failure)
        await asyncio.sleep(30)




def create_time(year, month, day, hour, minute):
    time_string = "{}-{}-{} {}:{}:0.0".format(year, month, day, hour, minute)
    time_string_for_save = "{}:{}:{}:{}:{}".format(year, month, day,hour, minute)
    return time_string_for_save


# Get Start Alarm Information Conversation :

@dispatcher.command_handler("/create_alarm")
def start_creating_alarm(bot, update):
    alarm = Alarm("", "", "", "", "", "", 5, "true")
    dispatcher.set_conversation_data(update, "alarm", alarm)
    user_peer = update.get_effective_user()
    alarm.user_id = user_peer.get_json_str()
    command = update.get_effective_message()
    bot.send_message(Message.GET_ALARM_NAME, user_peer, success_callback=success, failure_callback=failure)
    dispatcher.register_conversation_next_step_handler(update, MessageHandler(TextFilter(), get_alarm_name))


def get_alarm_name(bot, update):
    user_peer = update.get_effective_user()
    alarm_name = update.get_effective_message()
    dispatcher.get_conversation_data(update, "alarm").name = alarm_name.text
    bot.send_message(Message.GET_ALARM_MESSAGE, user_peer, success_callback=success, failure_callback=failure)
    dispatcher.set_conversation_data(update=update, key="my_data", value="my_value")
    dispatcher.register_conversation_next_step_handler(update, MessageHandler(TextFilter(), get_alarm_message))


def get_alarm_message(bot, update):
    user_peer = update.get_effective_user()
    alarm_message = update.get_effective_message()
    dispatcher.get_conversation_data(update, "alarm").message = alarm_message.text
    bot.send_message(Message.GET_ALARM_STOP_MESSAGE, user_peer, success_callback=success, failure_callback=failure)
    dispatcher.register_conversation_next_step_handler(update, MessageHandler(TextFilter(), get_alarm_stop_message))

def get_alarm_stop_message(bot, update):
    user_peer = update.get_effective_user()
    alarm_stop_message = update.get_effective_message()
    if check_stop_message_repetition(user_peer.get_json_str(), alarm_stop_message.text):
        bot.send_message(Message.STOP_MESSAGE_REPETIOTION, user_peer, success_callback=success, failure_callback=failure)
        dispatcher.register_conversation_next_step_handler(update, MessageHandler(TextFilter(), get_alarm_stop_message))
    else:
        dispatcher.get_conversation_data(update, "alarm").stop_message = alarm_stop_message.text
        bot.send_message(Message.GET_ALARM_PHOTO, user_peer, success_callback=success, failure_callback=failure)
        dispatcher.register_conversation_next_step_handler(update, MessageHandler(PhotoFilter(), get_alarm_photo))


def get_alarm_photo(bot, update):
    photo = update.get_effective_message()
    dispatcher.get_conversation_data(update, "alarm").photo = photo.get_json_str()
    user_peer = update.get_effective_user()
    bot.send_message(Message.GET_ALARM_YEAR, user_peer, success_callback=success, failure_callback=failure)
    dispatcher.set_conversation_data(update=update, key="my_data", value="my_value")
    dispatcher.register_conversation_next_step_handler(update, MessageHandler(TextFilter(), get_date_year))


def get_date_year(bot, update):
    user_peer = update.get_effective_user()
    year = update.get_effective_message().text
    dispatcher.set_conversation_data(update, "year",year )
    if int(year) < 1397:
        bot.send_message(Message.INVALID_INPUT, user_peer, success_callback=success, failure_callback=failure)
        dispatcher.register_conversation_next_step_handler(update, MessageHandler(TextFilter(), get_date_year))
    else:
        bot.send_message(Message.GET_ALARM_MONTH, user_peer, success_callback=success, failure_callback=failure)
        dispatcher.set_conversation_data(update=update, key="my_data", value="my_value")
        dispatcher.register_conversation_next_step_handler(update, MessageHandler(TextFilter(), get_date_month))



def get_date_month(bot, update):
    month = update.get_effective_message().text
    dispatcher.set_conversation_data(update, "month", month)
    user_peer = update.get_effective_user()
    if not (0 < int(month) < 13):
        bot.send_message(Message.INVALID_INPUT, user_peer, success_callback=success, failure_callback=failure)
        dispatcher.register_conversation_next_step_handler(update, MessageHandler(TextFilter(), get_date_month))
    else:
        bot.send_message(Message.GET_ALARM_DAY, user_peer, success_callback=success, failure_callback=failure)
        dispatcher.register_conversation_next_step_handler(update, MessageHandler(TextFilter(), get_date_day))


def get_date_day(bot, update):
    day = update.get_effective_message().text
    dispatcher.set_conversation_data(update, "day", day)
    user_peer = update.get_effective_user()
    if not ((0 < int(day) < 32 and 0 < int(dispatcher.get_conversation_data(update, "month")) < 7) or (0 < int(day) < 31 and 6 < int(dispatcher.get_conversation_data(update, "month")) < 13)) :
        bot.send_message(Message.INVALID_INPUT, user_peer, success_callback=success, failure_callback=failure)
        dispatcher.register_conversation_next_step_handler(update, MessageHandler(TextFilter(), get_date_day))
    else:
        bot.send_message(Message.GET_ALARM_HOUR, user_peer, success_callback=success, failure_callback=failure)
        dispatcher.register_conversation_next_step_handler(update, MessageHandler(TextFilter(), get_date_hour))


def get_date_hour(bot, update):
    hour = update.get_effective_message().text
    dispatcher.set_conversation_data(update, "hour", hour)
    user_peer = update.get_effective_user()
    if not 0 <= int(hour) < 24:
        bot.send_message(Message.INVALID_INPUT, user_peer, success_callback=success, failure_callback=failure)
        dispatcher.register_conversation_next_step_handler(update, MessageHandler(TextFilter(), get_date_hour))
    else:
        bot.send_message(Message.GET_ALARM_MINUTE, user_peer, success_callback=success, failure_callback=failure)
        dispatcher.register_conversation_next_step_handler(update, MessageHandler(TextFilter(), get_date_minute))


def get_date_minute(bot, update):
    minute = update.get_effective_message().text
    dispatcher.set_conversation_data(update, "minute", minute)
    user_peer = update.get_effective_user()
    if not 0 <= int(minute) < 60:
        bot.send_message(Message.INVALID_INPUT, user_peer, success_callback=success, failure_callback=failure)
        dispatcher.register_conversation_next_step_handler(update, MessageHandler(TextFilter(), get_date_minute))
    else:
        # print(create_time(year, month, day, hour, minute))
        dispatcher.get_conversation_data(update, "alarm").start_time = create_time(dispatcher.get_conversation_data(update, "year"), dispatcher.get_conversation_data(update, "month"),
                                       dispatcher.get_conversation_data(update, "day"), dispatcher.get_conversation_data(update, "hour"),
                                       dispatcher.get_conversation_data(update, "minute"))
        bot.send_message(Message.GET_ALARM_REPETITION_PERIOD, user_peer, success_callback=success, failure_callback=failure)
        dispatcher.register_conversation_next_step_handler(update, MessageHandler(TextFilter(), finish_creating_alarm))

def finish_creating_alarm(bot, update):
    user_peer = update.get_effective_user()
    period = update.get_effective_message()
    dispatcher.get_conversation_data(update, "alarm").repeat_period = period.text
    save_alarm(dispatcher.get_conversation_data(update, "alarm"))
    bot.send_message(Message.ALARM_CREATION_SUCCESS, user_peer, success_callback=success, failure_callback=failure)
    dispatcher.finish_conversation(update)





@dispatcher.command_handler("/add_debt")
def start_get_debt_conversation(bot, update):
    user_peer = update.get_effective_user()
    debt = Debt("", "", "", "", "", "","")
    dispatcher.set_conversation_data(update, "debt", debt)
    debt.user_id = user_peer.get_json_str()
    bot.send_message(Message.GET_DEBT_AMOUNT, user_peer, success_callback=success, failure_callback=failure)
    dispatcher.register_conversation_next_step_handler(update, MessageHandler(TextFilter(), get_amount))


def get_amount(bot, update):
    user_peer = update.get_effective_user()
    amount = update.get_effective_message()
    dispatcher.get_conversation_data(update, "debt").amount = amount.text
    bot.send_message(Message.GET_DEBT_CARD_NUMBER, user_peer, success_callback=success, failure_callback=failure)
    dispatcher.register_conversation_next_step_handler(update, MessageHandler(TextFilter(), get_card_number))


def get_card_number(bot, update):
    user_peer = update.get_effective_user()
    card_number = update.get_effective_message()
    dispatcher.get_conversation_data(update, "debt").card_number = card_number.text
    bot.send_message(Message.GET_CREDITOR_NAME, user_peer, success_callback=success, failure_callback=failure)
    dispatcher.register_conversation_next_step_handler(update, MessageHandler(TextFilter(), get_name_creditor))


def get_name_creditor(bot, update):
    user_peer = update.get_effective_user()
    creditor_name = update.get_effective_message()
    dispatcher.get_conversation_data(update, "debt").creditor_name = creditor_name.text
    bot.send_message(Message.GET_DEBT_YEAR, user_peer, success_callback=success, failure_callback=failure)
    dispatcher.register_conversation_next_step_handler(update, MessageHandler(TextFilter(), get_debt_date_year))


def get_debt_date_year(bot, update):
    user_peer = update.get_effective_user()
    debt_year = update.get_effective_message()
    dispatcher.set_conversation_data(update, "debt_year", debt_year.text)
    if int(debt_year.text) < 1397:
        bot.send_message(Message.INVALID_INPUT, user_peer, success_callback=success, failure_callback=failure)
        dispatcher.register_conversation_next_step_handler(update, MessageHandler(TextFilter(), get_debt_date_year))
    else:
        bot.send_message(Message.GET_DEBT_MONTH, user_peer, success_callback=success, failure_callback=failure)
        dispatcher.register_conversation_next_step_handler(update, MessageHandler(TextFilter(), get_debt_date_month))


def get_debt_date_month(bot,update):
    user_peer = update.get_effective_user()
    debt_month = update.get_effective_message()
    dispatcher.set_conversation_data(update, "debt_month", debt_month.text)
    if not (0 < int(debt_month.text) < 13):
        bot.send_message(Message.INVALID_INPUT, user_peer, success_callback=success, failure_callback=failure)
        dispatcher.register_conversation_next_step_handler(update, MessageHandler(TextFilter(), get_debt_date_month))
    else:
        bot.send_message(Message.GET_DEBT_DAY, user_peer, success_callback=success, failure_callback=failure)
        dispatcher.register_conversation_next_step_handler(update, MessageHandler(TextFilter(), get_debt_date_day))


def get_debt_date_day(bot, update):
    user_peer = update.get_effective_user()
    debt_day = update.get_effective_message()
    dispatcher.set_conversation_data(update, "debt_day", debt_day.text)
    if not ((0 < int(debt_day.text) < 32 and 0 < int(dispatcher.get_conversation_data(update, "debt_month")) < 7) or (
            0 < int(debt_day.text) < 31 and 6 < int(dispatcher.get_conversation_data(update, "debt_month")) < 13)):
        bot.send_message(Message.INVALID_INPUT, user_peer, success_callback=success, failure_callback=failure)
        dispatcher.register_conversation_next_step_handler(update, MessageHandler(TextFilter(), get_debt_date_day))
    else:
        dispatcher.get_conversation_data(update, "debt").date = "{}:{}:{}".format(dispatcher.get_conversation_data(update, "debt_year"), dispatcher.get_conversation_data(update, "debt_month"), dispatcher.get_conversation_data(update, "debt_day"))
        print(dispatcher.get_conversation_data(update, "debt").user_id)
        bot.send_message(Message.GET_DEBT_PHOTO, user_peer, success_callback=success, failure_callback=failure)
        dispatcher.register_conversation_next_step_handler(update, MessageHandler(PhotoFilter(), get_debt_photo))

def get_debt_photo(bot, update):
    user_peer = update.get_effective_user()
    photo = update.get_effective_message()
    save_photo(photo)
    dispatcher.get_conversation_data(update,"debt").photo_id = get_photo_id(photo)
    save_debt(dispatcher.get_conversation_data(update, "debt"))
    bot.send_message(Message.DEBT_CREATION_SECCESS, user_peer, success_callback=success, failure_callback=failure)
    dispatcher.finish_conversation(update)


@dispatcher.message_handler(TextFilter())
def check_stop_message(bot, update):
    user_peer = update.get_effective_user()
    input = update.get_effective_message()
    if search_stop_message(user_peer.get_json_str(), input.text):
        bot.send_message(update_alarm_activation(user_peer.get_json_str(), input.text), user_peer, success_callback=success, failure_callback=failure )



asyncio.ensure_future(send_alarm())
updater.run()