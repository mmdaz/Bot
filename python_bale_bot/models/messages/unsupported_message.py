import ujson as json_handler

from python_bale_bot.models.messages.base_message import BaseMessage
from python_bale_bot.models.constants.errors import Error

from python_bale_bot.models.constants.message_type import MessageType


class UnsupportedMessage(BaseMessage):
    def get_json_object(self):
        data = {
            "$type": MessageType.unsupported_message,
        }
        return data

    def get_json_str(self):
        return json_handler.dumps(self.get_json_object())

    @classmethod
    def load_from_json(cls, json):
        if isinstance(json, dict):
            json_dict = json
        elif isinstance(json, str):
            json_dict = json_handler.loads(json)
        else:
            raise ValueError(Error.unacceptable_json)

        return cls()
