from python_bale_bot.filters.filter import Filter


class DefaultFilter(Filter):
    def match(self, message):
        return True
