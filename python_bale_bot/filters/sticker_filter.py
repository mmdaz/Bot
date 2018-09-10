from python_bale_bot.models.messages.sticker_message import StickerMessage
from python_bale_bot.filters.filter import Filter


class StickerFilter(Filter):
    def match(self, message):
        return isinstance(message, StickerMessage)
