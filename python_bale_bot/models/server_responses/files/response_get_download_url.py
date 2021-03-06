import ujson as json_handler

from python_bale_bot.models.base_models.request_body import RequestBody
from python_bale_bot.models.constants.errors import Error


class ResponseGetDownloadUrl(RequestBody):
    def __init__(self, json):
        if isinstance(json, dict):
            json_dict = json
        elif isinstance(json, str):
            json_dict = json_handler.loads(json)
        else:
            raise ValueError(Error.unacceptable_json)

        self.url = json_dict.get("url", None)
