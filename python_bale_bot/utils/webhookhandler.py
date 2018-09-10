import logging
# from telegram import Update
from future.utils import bytes_to_native_str
from threading import Lock
from python_bale_bot.utils.logger import Logger

try:
    import ujson as json
except ImportError:
    import json
try:
    import BaseHTTPServer
except ImportError:
    import http.server as BaseHTTPServer

logging.getLogger(__name__).addHandler(logging.NullHandler())


class _InvalidPost(Exception):

    def __init__(self, http_code):
        self.http_code = http_code
        super(_InvalidPost, self).__init__()


class WebhookServer(BaseHTTPServer.HTTPServer, object):

    def __init__(self, server_address, RequestHandlerClass, incoming_queue, webhook_path, bot):
        super(WebhookServer, self).__init__(server_address, RequestHandlerClass)
        self.logger = Logger.get_logger()
        self.incoming_queue = incoming_queue
        self.webhook_path = webhook_path
        self.bot = bot
        self.is_running = False
        self.server_lock = Lock()
        self.shutdown_lock = Lock()

    def serve_forever(self, poll_interval=0.5):
        with self.server_lock:
            self.is_running = True
            self.logger.debug('Webhook Server started.')
            super(WebhookServer, self).serve_forever(poll_interval)
            self.logger.debug('Webhook Server stopped.')

    def shutdown(self):
        with self.shutdown_lock:
            if not self.is_running:
                self.logger.warning('Webhook Server already stopped.')
                return
            else:
                super(WebhookServer, self).shutdown()
                self.is_running = False

    def handle_error(self, request, client_address):
        """Handle an error gracefully."""
        self.logger.debug('Exception happened during processing of request from %s',
                          client_address, exc_info=True)


# WebhookHandler, process webhook calls
# Based on: https://github.com/eternnoir/pyTelegramBotAPI/blob/master/
# examples/webhook_examples/webhook_cpython_echo_bot.py
class WebhookHandler(BaseHTTPServer.BaseHTTPRequestHandler, object):
    server_version = 'WebhookHandler/1.0'

    def __init__(self, request, client_address, server):
        self.logger = Logger.get_logger()
        super(WebhookHandler, self).__init__(request, client_address, server)

    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        self.send_response(200)
        self.end_headers()

    def do_POST(self):
        self.logger.debug('Webhook triggered')
        try:
            self._validate_post()
            c_len = self._get_content_len()
        except _InvalidPost as e:
            self.send_error(e.http_code)
            self.end_headers()
        else:
            buf = self.rfile.read(c_len)
            json_string = bytes_to_native_str(buf)

            self.send_response(200)
            self.end_headers()
            # update = Update.de_json(json.loads(json_string), self.server.bot)
            update_json = json.loads(json_string)
            self.logger.debug("[transport] receiving on Webhook:  {0} ".format(update_json))
            # self.server.update_queue.put(update)
            self.server.incoming_queue.put(update_json)

    def _validate_post(self):
        if not (self.path == self.server.webhook_path and 'content-type' in self.headers and
                self.headers['content-type'] == 'application/json'):
            raise _InvalidPost(403)

    def _get_content_len(self):
        c_len = self.headers.get('content-length')
        if c_len is None:
            raise _InvalidPost(411)
        try:
            c_len = int(c_len)
        except ValueError:
            raise _InvalidPost(403)
        if c_len < 0:
            raise _InvalidPost(403)
        return c_len

    def log_message(self, format, *args):
        """Log an arbitrary message.

        This is used by all other logging functions.

        It overrides ``BaseHTTPRequestHandler.log_message``, which logs to ``sys.stderr``.

        The first argument, FORMAT, is a format string for the message to be logged.  If the format
        string contains any % escapes requiring parameters, they should be specified as subsequent
        arguments (it's just like printf!).

        The client ip is prefixed to every message.

        """
        self.logger.debug("%s - - %s" % (self.address_string(), format % args))
