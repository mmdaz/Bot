from python_bale_bot.models.messages.banking.bank_message import BankMessage
from python_bale_bot.filters.filter import Filter


class BankMessageFilter(Filter):
    def match(self, message):
        return isinstance(message, BankMessage)
