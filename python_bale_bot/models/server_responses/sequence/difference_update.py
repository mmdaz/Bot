import ujson as json_handler

from python_bale_bot.models.base_models.fat_seq_update import FatSeqUpdate
from python_bale_bot.models.base_models.response_body import ResponseBody
from python_bale_bot.models.constants.errors import Error


class DifferenceUpdate(ResponseBody):
    def __init__(self, json):
        if isinstance(json, dict):
            json_dict = json
        elif isinstance(json, str):
            json_dict = json_handler.loads(json)
        else:
            raise ValueError(Error.unacceptable_json)

        self.seq = json_dict.get("seq", None)
        self.updates = [FatSeqUpdate(update) for update in json_dict.get("updates", None)]
        self.need_more = json_dict.get("needMore", None)
