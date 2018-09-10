"""This module contains an object that represents Bale errors."""


def _lstrip_str(in_s, lstr):
    """
    Args:
        in_s (:obj:`str`): in string
        lstr (:obj:`str`): substr to strip from left side

    Returns:
        str:

    """
    if in_s.startswith(lstr):
        res = in_s[len(lstr):]
    else:
        res = in_s
    return res


class BaleError(Exception):
    def __init__(self, message):
        super(BaleError, self).__init__()

        msg = _lstrip_str(message, 'Error: ')
        msg = _lstrip_str(msg, '[Error]: ')
        msg = _lstrip_str(msg, 'Bad Request: ')
        if msg != message:
            # api_error - capitalize the msg...
            msg = msg.capitalize()
        self.message = msg

    def __str__(self):
        return '%s' % (self.message)



class InvalidToken(BaleError):

    def __init__(self):
        super(InvalidToken, self).__init__('Invalid token')


class NetworkError(BaleError):
    pass


class BadRequest(NetworkError):
    pass


class TimedOut(NetworkError):

    def __init__(self):
        super(TimedOut, self).__init__('Timed out')


class RetryAfter(BaleError):
    """
    Args:
        retry_after (:obj:`int`):

    """

    def __init__(self, retry_after):
        super(RetryAfter,
              self).__init__('Flood control exceeded. Retry in {} seconds'.format(retry_after))
        self.retry_after = float(retry_after)
