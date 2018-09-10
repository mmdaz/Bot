import collections
import functools
import traceback

import requests
from requests.adapters import HTTPAdapter

from python_bale_bot.config import Config
from python_bale_bot.models.base_models import response
from python_bale_bot.models.client_requests import *

from python_bale_bot.models.base_models import BotQuotedMessage, FatSeqUpdate, Request
from python_bale_bot.models.client_requests.sequence.get_last_sequence import GetLastSequence
from python_bale_bot.models.client_requests.webhook.register_webhook import RegisterWebhook
from python_bale_bot.models.client_requests.webhook.unregister_webhook import UnRegisterWebhook
from python_bale_bot.models.constants.request_to_response_mapper import RequestToResponseMapper
from python_bale_bot.models.constants.service_type import ServiceType
from python_bale_bot.models.messages import BaseMessage, TextMessage
from python_bale_bot.utils.util_functions import get_file_crc32, get_file_size, get_file_buffer
from python_bale_bot.utils.logger import Logger
from python_bale_bot.dispatcher import run_async

logger = Logger.get_logger()


def send_request(func):
    @functools.wraps(func)
    def decorator(self, *args, **kwargs):
        request = func(self, *args, **kwargs)
        request_body = request.body
        response_body_module, response_body_class = RequestToResponseMapper.get_response(request_body)
        if kwargs.get('success_callback'):
            success_callback = kwargs.get('success_callback') if isinstance(kwargs.get('success_callback'),
                                                                            collections.Callable) else None
        else:
            success_callback = None

        if kwargs.get('failure_callback'):
            failure_callback = kwargs.get('failure_callback') if isinstance(kwargs.get('failure_callback'),
                                                                            collections.Callable) else None
        else:
            failure_callback = None

        if kwargs.get('kwargs'):
            func_kwargs = kwargs.get('kwargs')
        else:
            func_kwargs = {}
        logger.debug('[transport] sending :  {}'.format(request.get_json_object()))
        res = None
        try:
            res = self._session.post(
                url="{0}/{1}".format(self.base_url, self.token),
                json=request.get_json_object())
            logger.debug('[transport] receiving :  {}'.format(res.json()))
            bale_response = response.Response(res.json())
            bale_response.create_body(response_body_module, response_body_class)
        except Exception as ex:
            logger.error(ex, extra={"tag": "err"})
            traceback.print_exc()
            bot_timeout_json = {"body": {"tag": "CLIENT_INTERNAL_ERROR"}}
            bale_response = response.Response(bot_timeout_json)
        if bale_response.is_bot_error():
            if failure_callback:
                failure_callback(bale_response, func_kwargs)
        else:
            if success_callback:
                success_callback(bale_response, func_kwargs)
        return res

    return decorator


class Bot:
    def __init__(self, token, user_id, base_url, timeout=5, adapter=None, session=None):
        self.token = token
        self.user_id = user_id
        if base_url is None:
            self.base_url = Config.base_url

        self.timeout = timeout

        if session is None or adapter is None:
            self.adapter = HTTPAdapter()
            self._session = requests.Session()
            self._session.headers.update({'Connection': 'keep-alive'})
            self._session.mount(self.base_url, self.adapter)
        else:
            self.adapter = adapter
            self._session = session
            self._session.headers.update({'Connection': 'keep-alive'})
            self._session.mount(self.base_url, self.adapter)

    '''no need for decorator it uses send message function and it is decorated'''

    def reply(self, update, message, success_callback=None, failure_callback=None, **kwargs):
        if isinstance(update, FatSeqUpdate) and update.is_message_update():
            message_id = update.body.random_id
            user_peer = update.get_effective_user()
            if isinstance(message, BaseMessage):
                self.send_message(message, user_peer,
                                  BotQuotedMessage(message_id, user_peer),
                                  success_callback=success_callback,
                                  failure_callback=failure_callback,
                                  **kwargs)
            else:
                self.send_message(TextMessage(message), user_peer,
                                  BotQuotedMessage(message_id, user_peer),
                                  success_callback=success_callback,
                                  failure_callback=failure_callback,
                                  **kwargs)

    def respond(self, update, message, success_callback=None, failure_callback=None, **kwargs):
        user_peer = update.get_effective_user()
        if isinstance(message, BaseMessage):
            self.send_message(message, user_peer,
                              success_callback=success_callback,
                              failure_callback=failure_callback,
                              **kwargs)
        else:
            self.send_message(TextMessage(message), user_peer,
                              success_callback=success_callback,
                              failure_callback=failure_callback,
                              **kwargs)

    # messaging

    @send_request
    def send_message(self, message, peer, quoted_message=None, random_id=None, success_callback=None,
                     failure_callback=None, **kwargs):
        receiver = peer
        request_body = SendMessage(message=message, receiver_peer=receiver,
                                   quoted_message=quoted_message, random_id=random_id)
        request = Request(service=ServiceType.Messaging, body=request_body)
        return request

    # sequence-update

    @send_request
    def get_difference(self, seq, how_many, success_callback=None, failure_callback=None, **kwargs):
        request_body = GetDifference(seq=seq, how_many=how_many)
        request = Request(service=ServiceType.SequenceUpdate, body=request_body)
        return request

    # last_sequence

    @send_request
    def get_last_seq(self, success_callback=None, failure_callback=None, **kwargs):
        request_body = GetLastSequence()
        request = Request(service=ServiceType.SequenceUpdate, body=request_body)
        return request

    # webhook
    @send_request
    def set_webhook(self, endpoint=None, timeout=None, success_callback=None, failure_callback=None, **kwargs):
        # Backwards-compatibility: 'url' used to be named 'webhook_url'
        request_body = RegisterWebhook(self.user_id, endpoint)
        request = Request(service=ServiceType.WebHooks, body=request_body)
        return request

    @send_request
    def delete_webhook(self, timeout=None, success_callback=None, failure_callback=None, **kwargs):
        # Backwards-compatibility: 'url' used to be named 'webhook_url'
        request_body = UnRegisterWebhook(self.user_id)
        request = Request(service=ServiceType.WebHooks, body=request_body)
        return request

    # file

    @send_request
    def get_file_download_url(self, file_id, user_id, file_type, file_version=1, is_server=False,
                              is_resume_upload=False, success_callback=None, failure_callback=None, **kwargs):
        request_body = GetFileDownloadUrl(file_id, user_id, file_type, file_version, is_server, is_resume_upload)
        request = Request(service=ServiceType.Files, body=request_body)
        return request

    @send_request
    def get_file_upload_url(self, size, crc, file_type, is_server=False, success_callback=None, failure_callback=None,
                            **kwargs):
        request_body = GetFileUploadUrl(size, crc, file_type, is_server)
        request = Request(service=ServiceType.Files, body=request_body)
        return request

    def download_file(self, file_id, user_id, file_type="file", success_callback=None, failure_callback=None, **kwargs):
        success_callback = success_callback if isinstance(success_callback, collections.Callable) else None
        failure_callback = failure_callback if isinstance(failure_callback, collections.Callable) else None

        def file_download_url_success(result, user_data):
            if user_data:
                callback_user_data = user_data
            else:
                callback_user_data = {}
            url = result.body.url

            @run_async
            def get_data(download_url):
                try:
                    with requests.session() as session:
                        with session.get(download_url) as res:
                            if res.status_code == 200:
                                if success_callback:
                                    callback_user_data.update(byte_stream=res.content)
                                    success_callback(None, callback_user_data)
                            else:
                                if failure_callback:
                                    failure_callback(None, callback_user_data)
                except Exception as ex:
                    logger.error(ex, extra={"tag": "err"})
                    bot_timeout_json = {"body": {"tag": "CLIENT_INTERNAL_ERROR_ON_DOWNLOAD {}".format(download_url)}}
                    logger.error(bot_timeout_json, extra={"tag": "err"})
                    traceback.print_exc()
                    if failure_callback:
                        failure_callback(None, callback_user_data)

            get_data(url)

        def file_download_url_failure(result, user_data):
            if failure_callback:
                failure_callback(result, user_data)

        self.get_file_download_url(file_id, user_id, file_type,
                                   success_callback=file_download_url_success,
                                   failure_callback=file_download_url_failure)

    def upload_file(self, file, file_type, success_callback=None, failure_callback=None, **kwargs):
        success_callback = success_callback if isinstance(success_callback, collections.Callable) else None
        failure_callback = failure_callback if isinstance(failure_callback, collections.Callable) else None

        buffer = get_file_buffer(file=file)
        if buffer is None:
            if failure_callback:
                failure_callback(None)
            return

        file_size = get_file_size(buffer)
        file_crc32 = get_file_crc32(buffer)

        def file_upload_url_success(result, user_data):
            file_id = result.body.file_id
            user_id = result.body.user_id
            url = result.body.url
            dup = result.body.dup
            if user_data:
                callback_user_data = user_data
            else:
                callback_user_data = {}
            data = buffer

            @run_async
            def upload_data():
                try:
                    with requests.session() as session:
                        with session.put(url=url, data=data, headers={'filesize': str(file_size)}) as response:
                            if response.status_code == 200:
                                if success_callback:
                                    callback_user_data.update(file_id=file_id, user_id=user_id, url=url, dup=dup)
                                    success_callback(None, callback_user_data)
                            else:
                                if failure_callback:
                                    failure_callback(None, callback_user_data)
                except Exception as ex:
                    logger.error(ex, extra={"tag": "err"})
                    bot_timeout_json = {"body": {"tag": "CLIENT_INTERNAL_ERROR_ON_UPLOAD_FILE {}".format(file_id)}}
                    logger.error(bot_timeout_json, extra={"tag": "err"})
                    traceback.print_exc()
                    if failure_callback:
                        failure_callback(None)

            upload_data()

        def file_upload_url_failure(result, user_data):
            if failure_callback:
                failure_callback(result, user_data)

        self.get_file_upload_url(size=file_size, crc=file_crc32, file_type=file_type,
                                 success_callback=file_upload_url_success,
                                 failure_callback=file_upload_url_failure)
