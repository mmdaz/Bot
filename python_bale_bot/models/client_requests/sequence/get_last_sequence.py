import ujson as json_handler

from python_bale_bot.models.base_models.request_body import RequestBody
from python_bale_bot.models.constants.request_type import RequestType


class GetLastSequence(RequestBody):
    def __init__(self):
        self.seq = "input"

    def get_json_object(self):
        data = {
            "$type": RequestType.get_last_seq,
            "seq": self.seq
        }
        return data

    def get_json_str(self):
        return json_handler.dumps(self.get_json_object())
