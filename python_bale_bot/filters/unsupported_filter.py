from python_bale_bot.models.messages.unsupported_message import UnsupportedMessage
from python_bale_bot.filters.filter import Filter


class UnsupportedFilter(Filter):
    def match(self, message):
        return isinstance(message, UnsupportedMessage)
