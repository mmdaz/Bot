from python_bale_bot.models.messages.voice_message import VoiceMessage
from python_bale_bot.filters.filter import Filter


class VoiceFilter(Filter):
    def match(self, message):
        return isinstance(message, VoiceMessage)
