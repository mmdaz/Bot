from python_bale_bot.models.messages.photo_message import PhotoMessage
from python_bale_bot.filters.filter import Filter


class PhotoFilter(Filter):
    def match(self, message):
        return isinstance(message, PhotoMessage)
