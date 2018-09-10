from python_bale_bot.models.messages.json_message import JsonMessage
from python_bale_bot.filters.filter import Filter


class JsonFilter(Filter):
    def match(self, message):
        return isinstance(message, JsonMessage)
