import asyncio
from balebot.handlers import *
from balebot.filters import *
from balebot.models.base_models import Peer
from balebot.models.messages import *
from balebot.updater import Updater
from balebot.config import Config

# Config.real_time_fetch_updates=True

updater = Updater (token="d821ecf310fde3a4fe485543539c53acebe3c7ae" ,loop=asyncio.get_event_loop())
dispatcher = updater.dispatcher


def success(result):
    print("success : ", result)


def failure(result):
    print("failure : ", result)


@dispatcher.message_handler(filters=[TextFilter(keywords=["iran", "tehran", "سلام"], pattern="^hello(.)+"),
                                     TemplateResponseFilter(keywords=["hellooo"])])
def text_received(bot, update):
    message = update.get_effective_message()
    user_peer = update.get_effective_user()
    bot.send_message(message, user_peer, success_callback=success, failure_callback=failure)


@dispatcher.message_handler([DocumentFilter(), PhotoFilter(), VoiceFilter(), VideoFilter(), StickerFilter()])
def start_command(bot, update):
    message = update.get_effective_message()
    print("received messages forwarded to sender.")
    bot.reply(update, message, success_callback=success, failure_callback=failure)


@dispatcher.command_handler("/start")
def start_command(bot, update):
    message = update.get_effective_message()
    bot.respond(update, message, success_callback=success, failure_callback=failure)


@dispatcher.command_handler(["/skip", "/help"])
def skip_or_help_command_received(bot, update):
    bot.reply(update, "do you need help?\nor you want to skip?", success_callback=success, failure_callback=failure)


@dispatcher.error_handler()
def error_handler(bot, update, error):
    if update:
        print(update)
    print(error, "  :  handled by error_handler")


updater.run()