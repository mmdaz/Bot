import ujson as json_handler

from python_bale_bot.models.base_models.response_body import ResponseBody
from python_bale_bot.models.constants.errors import Error


class WebhookRegisteredResponse(ResponseBody):
    def __init__(self, json):
        if isinstance(json, dict):
            json_dict = json
        elif isinstance(json, str):
            json_dict = json_handler.loads(json)
        else:
            raise ValueError(Error.unacceptable_json)

        self.data = json_dict.get("data", None)
        self.code = json_dict.get("code", None)
        self.tag = json_dict.get("tag", None)
        self.retryIn = json_dict.get("retryIn", None)
