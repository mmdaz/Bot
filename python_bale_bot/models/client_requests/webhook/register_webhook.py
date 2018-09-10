from python_bale_bot.models.constants.request_type import RequestType
from python_bale_bot.models.constants.errors import Error
from python_bale_bot.models.base_models.request_body import RequestBody
import ujson as json_handler


class RegisterWebhook(RequestBody):
    def __init__(self, user_id, end_point):

        if isinstance(user_id, int) and isinstance(end_point, str) :
            self.user_id=user_id
            self.end_point = end_point


        else:
            raise ValueError(Error.unacceptable_object_type)

    def get_json_object(self):

        data = {
            "$type": RequestType.register_webhook,
            "userId":self.user_id,
            "endpoint": self.end_point
        }

        return data

    def get_json_str(self):
        return json_handler.dumps(self.get_json_object())
