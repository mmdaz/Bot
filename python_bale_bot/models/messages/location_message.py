import ujson as json_handler

from python_bale_bot.models.constants.raw_json_type import RawJsonType
from python_bale_bot.models.base_models.raw_json import RawJson
from python_bale_bot.models.messages.base_message import BaseMessage
from python_bale_bot.models.constants.errors import Error
from python_bale_bot.models.constants.message_type import MessageType


class LocationMessage(RawJson, BaseMessage):
    def __init__(self, latitude, longitude):
        self.latitude = float(latitude)
        self.longitude = float(longitude)

    def get_json_object(self):

        data = {
            "$type": MessageType.json_message,
            "rawJson": json_handler.dumps({
                "dataType": RawJsonType.location,
                "data": {
                    RawJsonType.location: {
                        "latitude": self.latitude,
                        "longitude": self.longitude
                    }
                }
            })
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

        data = json_dict.get('data', None)
        location = data.get(RawJsonType.location, None)
        latitude = location.get('latitude', None)
        longitude = location.get('longitude', None)

        return cls(latitude=latitude, longitude=longitude)
