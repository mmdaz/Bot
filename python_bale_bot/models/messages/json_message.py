import ujson as json_handler

from python_bale_bot.models.base_models.raw_json import RawJson
from python_bale_bot.models.messages.base_message import BaseMessage
from python_bale_bot.models.constants.errors import Error
from python_bale_bot.models.factories import raw_json_factory
from python_bale_bot.models.constants.message_type import MessageType


class JsonMessage(BaseMessage):
    def __init__(self, raw_json):
        if isinstance(raw_json, RawJson):
            self.raw_json = raw_json

    def get_json_object(self):

        data = {
            "$type": MessageType.json_message,
            "rawJson": self.raw_json.get_json_str()

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

        raw_json_dict = json_handler.loads(json_dict.get('rawJson', None))
        raw_json = raw_json_factory.RawJsonFactory.create_raw_json(raw_json_dict)

        if raw_json is None:
            raise ValueError(Error.none_or_invalid_attribute)

        return cls(raw_json=raw_json)
