from python_bale_bot.models.messages.location_message import LocationMessage
from python_bale_bot.models.messages.json_message import JsonMessage
from python_bale_bot.filters.filter import Filter


class LocationFilter(Filter):
    def match(self, message):
        if isinstance(message, JsonMessage):
            raw_json = message.raw_json
            return isinstance(raw_json, LocationMessage)
        else:
            return False
