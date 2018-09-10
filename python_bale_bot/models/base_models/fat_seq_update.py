import ujson as json_handler
from python_bale_bot.models.constants.errors import Error

from python_bale_bot.models.base_models.group import Group
from python_bale_bot.models.base_models.user import User
from python_bale_bot.models.factories import update_body_factory
from python_bale_bot.models.server_updates.bot_read_update_body import BotReadUpdate
from python_bale_bot.models.server_updates.message_update_body import MessageUpdate
from python_bale_bot.models.server_updates.raw_update_body import RawUpdate

from python_bale_bot.models.server_updates.bot_received_update_body import BotReceivedUpdate


class FatSeqUpdate:
    def __init__(self, json):
        if isinstance(json, dict):
            json_dict = json
        elif isinstance(json, str):
            json_dict = json_handler.loads(json)
        else:
            raise ValueError(Error.unacceptable_json)

        self.seq = json_dict.get("seq", None)

        self.body = update_body_factory.UpdateBodyFactory.create_update_body(json_dict.get("body", None))

        temp_users = json_dict.get("users", None)
        self.users = [User.load_from_json(user[1]) for user in temp_users]

        temp_groups = json_dict.get("groups", None)
        self.groups = [Group.load_from_json(group[1]) for group in temp_groups]

    def is_message_update(self):
        return isinstance(self.body, MessageUpdate)

    def is_read_update(self):
        return isinstance(self.body, BotReadUpdate)

    def is_received_update(self):
        return isinstance(self.body, BotReceivedUpdate)

    def is_raw_update(self):
        return isinstance(self.body, RawUpdate)

    def get_effective_user(self):
        user = None
        if self.is_message_update():
            user = self.body.peer
        elif self.is_received_update():
            user = self.body.peer
        elif self.is_read_update():
            user = self.body.peer
        return user

    def get_effective_message(self):
        message = None
        if self.is_message_update():
            message = self.body.message
        return message
