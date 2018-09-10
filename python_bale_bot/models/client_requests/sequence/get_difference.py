import ujson as json_handler

from python_bale_bot.models.base_models.request_body import RequestBody
from python_bale_bot.models.constants.request_type import RequestType


class GetDifference(RequestBody):
    def __init__(self, seq, how_many):
        self.seq = int(seq) if seq else 0
        self.how_many = how_many

    def get_json_object(self):
        data = {
            "$type": RequestType.get_difference,
            "seq": self.seq,
            "howMany": self.how_many,
        }

        return data

    def get_json_str(self):
        return json_handler.dumps(self.get_json_object())
