from python_bale_bot.models.messages.video_message import VideoMessage
from python_bale_bot.filters.filter import Filter


class VideoFilter(Filter):
    def match(self, message):
        return isinstance(message, VideoMessage)
