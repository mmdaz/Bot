from python_bale_bot.models.messages.contact_message import ContactMessage
from python_bale_bot.models.messages.json_message import JsonMessage
from python_bale_bot.filters.filter import Filter


class ContactFilter(Filter):
    def match(self, message):
        if isinstance(message, JsonMessage):
            raw_json = message.raw_json
            return isinstance(raw_json, ContactMessage)
        else:
            return False
