from python_bale_bot.models.constants.request_type import RequestType
from python_bale_bot.models.constants.errors import Error
from python_bale_bot.models.base_models.request_body import RequestBody
import ujson as json_handler


class UnRegisterWebhook(RequestBody):
    def __init__(self, user_id):

        if isinstance(user_id, int):
            self.user_id = user_id


        else:
            raise ValueError(Error.unacceptable_object_type)

    def get_json_object(self):

        data = {
            "$type": RequestType.unregister_webhook,
            "userId": self.user_id
        }

        return data

    def get_json_str(self):
        return json_handler.dumps(self.get_json_object())
