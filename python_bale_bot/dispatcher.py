import time
import traceback
import weakref
from functools import wraps
from queue import Queue, Empty
from threading import Lock, Event, BoundedSemaphore, Thread, current_thread
from uuid import uuid4

from python_bale_bot.config import Config
from python_bale_bot.error import BaleError
from python_bale_bot.filters import DefaultFilter, TextFilter
from python_bale_bot.handlers import Handler, CommandHandler, MessageHandler
from python_bale_bot.models.base_models import Response
from python_bale_bot.models.base_models.fat_seq_update import FatSeqUpdate
from python_bale_bot.models.factories import server_update_factory
from python_bale_bot.models.messages import TextMessage
from python_bale_bot.utils.logger import Logger
from python_bale_bot.utils.promise import Promise


def run_async(func):
    """Function decorator that will run the function in a new thread.

    Will run :attr:`telegram.ext.Dispatcher.run_async`.

    Using this decorator is only possible when only a single Dispatcher exist in the system.

    Note: Use this decorator to run handlers asynchronously.

    """

    @wraps(func)
    def async_func(*args, **kwargs):
        return Dispatcher.get_instance().run_async(func, *args, **kwargs)

    return async_func


class DispatcherHandlerStop(Exception):
    """Raise this in handler to prevent execution any other handler (even in different group)."""
    pass


class Dispatcher(object):
    __singleton_lock = Lock()
    __singleton_semaphore = BoundedSemaphore()
    __singleton = None
    logger = Logger.get_logger()

    def __init__(self, bot, incoming_queue, workers=Config.default_worker_numbers, exception_event=None, job_queue=None):
        self.bot = bot

        self.logger = Logger.get_logger()
        self.incoming_queue = incoming_queue
        self.timeout = Config.request_timeout
        # self.job_queue = job_queue
        self.workers = workers

        self.message_handlers = []
        self.error_handlers = []
        self.read_handler_object = None
        self.default_handler_object = None

        self.running = False

        self.__stop_event = Event()
        self.__exception_event = exception_event or Event()
        self.__async_queue = Queue()
        self.__async_threads = set()

        self.conversation_next_step_handlers = {}
        self.conversation_data = {}

        # self.is_batch_updates_processed = True
        # self.last_seq = None
        # self.real_time_fetch_updates = Config.real_time_fetch_updates
        # self.continue_last_processed_seq = Config.continue_last_processed_seq
        # self.timeInterval = Config.timeInterval
        # self.last_poll_request_time = 0
        # self.updates_number = Config.updates_number

        # For backward compatibility, we allow a "singleton" mode for the dispatcher. When there's
        # only one instance of Dispatcher, it will be possible to use the `run_async` decorator.
        with self.__singleton_lock:
            if self.__singleton_semaphore.acquire(blocking=False):
                self._set_singleton(self)
            else:
                self._set_singleton(None)

        @self.message_handler(TextFilter(pattern=r"{}*".format(Config.monitoring_hash)))
        def handle_monitoring_msg(handler_bot, update):
            monitoring_message = update.get_effective_message()
            monitoring_text = monitoring_message.text
            result_text = str(monitoring_text.split(Config.monitoring_hash)[1])
            result_message = TextMessage(text=result_text)
            handler_bot.respond(update=update, message=result_message)

    def _init_async_threads(self, base_name, workers):
        base_name = '{}_'.format(base_name) if base_name else ''

        for i in range(workers):
            thread = Thread(target=self._pooled, name='{}{}'.format(base_name, i))
            self.__async_threads.add(thread)
            thread.start()

    @classmethod
    def _set_singleton(cls, val):
        cls.logger.debug('Setting singleton dispatcher as %s', val)
        cls.__singleton = weakref.ref(val) if val else None

    @classmethod
    def get_instance(cls):
        """Get the singleton instance of this class.

        Returns:
            :class:`telegram.ext.Dispatcher`

        Raises:
            RuntimeError

        """
        if cls.__singleton is not None:
            return cls.__singleton()
        else:
            raise RuntimeError('{} not initialized or multiple instances exist'.format(
                cls.__name__))

    def _pooled(self):
        thr_name = current_thread().getName()
        while 1:
            promise = self.__async_queue.get()

            # If unpacking fails, the thread pool is being closed from Updater._join_async_threads
            if not isinstance(promise, Promise):
                self.logger.debug("Closing run_async thread %s/%d", thr_name,
                                  len(self.__async_threads))
                break
            self.logger.debug("promise run_async in  thread  %s/ max thread number is %d", thr_name,
                              len(self.__async_threads))
            promise.run()
            if isinstance(promise.exception, DispatcherHandlerStop):
                self.logger.warning(
                    'DispatcherHandlerStop is not supported with async functions; func: %s',
                    promise.pooled_function.__name__)

    def run_async(self, func, *args, **kwargs):
        """Queue a function (with given args/kwargs) to be run asynchronously.

        Args:
            func (:obj:`callable`): The function to run in the thread.
            *args (:obj:`tuple`, optional): Arguments to `func`.
            **kwargs (:obj:`dict`, optional): Keyword arguments to `func`.

        Returns:
            Promise

        """
        # TODO: handle exception in async threads
        #       set a threading.Event to notify caller thread
        promise = Promise(func, args, kwargs)
        self.__async_queue.put(promise)
        return promise

    def start(self, ready=None):
        if self.running:
            self.logger.warning('already running')
            if ready is not None:
                ready.set()
            return

        if self.__exception_event.is_set():
            msg = 'reusing dispatcher after exception event is forbidden'
            self.logger.error(msg)
            raise BaleError(msg)

        self._init_async_threads(uuid4(), self.workers)
        self.running = True
        self.logger.debug('Dispatcher started')

        if ready is not None:
            ready.set()

        while 1:
            try:
                # Pop update from update queue.
                update = self.incoming_queue.get(True, 1)
            except Empty:
                if self.__stop_event.is_set():
                    self.logger.debug('orderly stopping')
                    break
                elif self.__exception_event.is_set():
                    self.logger.critical('stopping due to exception in another thread')
                    break
                continue

            self.logger.debug('Processing Update: %s' % update)
            # update_message_data = update_message.data
            # update_message_json = json_handler.loads(update_message_data)
            self.process_update(update)

        self.running = False
        self.logger.debug('Dispatcher thread stopped')

    def stop(self):
        """Stops the thread."""
        if self.running:
            self.__stop_event.set()
            while self.running:
                time.sleep(0.1)
            self.__stop_event.clear()
        self.running = False
        # async threads must be join()ed only after the dispatcher thread was joined,
        # otherwise we can still have new async threads dispatched
        threads = list(self.__async_threads)
        total = len(threads)

        # Stop all threads in the thread pool by put()ting one non-tuple per thread
        for i in range(total):
            self.__async_queue.put(None)

        for i, thr in enumerate(threads):
            self.logger.debug('Waiting for async thread {0}/{1} to end'.format(i + 1, total))
            thr.join()
            self.__async_threads.remove(thr)
            self.logger.debug('async thread {0}/{1} has ended'.format(i + 1, total))

    @property
    def has_running_threads(self):
        return self.running or bool(self.__async_threads)

    def process_update(self, update_json):

        update = server_update_factory.ServerUpdateFactory.create_update(update_json)
        if isinstance(update, FatSeqUpdate):
            self.process_fat_seq_update(update)

    def process_fat_seq_update(self, update):
        if update.is_message_update():
            user_peer = update.get_effective_user()
            user_id = user_peer.peer_id

            message_handled = False

            if (user_id in self.conversation_next_step_handlers) and self.conversation_next_step_handlers.get(
                    user_id, None):

                default_conversation_handler = None

                for handler in self.conversation_next_step_handlers.get(user_id, None):

                    if not handler.is_default_handler():
                        try:
                            if handler.check_update(update):
                                handler.handle_update(self, update)
                                message_handled = True
                                break
                        except Exception as ex:
                            self.logger.error(ex, extra={"tag": "err"})
                            traceback.print_exc()

                            try:
                                bot_timeout_json = {"body": {"tag": "CLIENT_INTERNAL_ERROR"}}
                                error_response = Response(bot_timeout_json)
                                self.dispatch_error(error_response, ex)
                            except Exception as ex:
                                self.logger.error(ex, extra={"tag": "err"})
                                traceback.print_exc()
                    else:
                        default_conversation_handler = handler

                if (not message_handled) and default_conversation_handler:
                    if default_conversation_handler.check_update(update):
                        default_conversation_handler.handle_update(self, update)

            else:
                for handler in self.message_handlers:
                    try:
                        if handler.check_update(update):
                            handler.handle_update(self, update)
                            message_handled = True
                            break
                    except Exception as ex:
                        self.logger.error(ex, extra={"tag": "err"})
                        traceback.print_exc()

                        try:
                            bot_timeout_json = {"body": {"tag": "CLIENT_INTERNAL_ERROR"}}
                            error_response = Response(bot_timeout_json)
                            self.dispatch_error(error_response, ex)
                        except Exception as ex:
                            self.logger.error(ex, extra={"tag": "err"})
                            traceback.print_exc()

                if (not message_handled) and self.default_handler_object:
                    if self.default_handler_object.check_update(update):
                        self.default_handler_object.handle_update(self, update)
            return

        elif update.is_read_update():
            if self.read_handler_object:
                try:
                    if self.read_handler_object.check_update(update):
                        self.read_handler_object.handle_update(self, update)
                except Exception as ex:
                    self.logger.error(ex, extra={"tag": "err"})
                    traceback.print_exc()

                    try:
                        bot_timeout_json = {"body": {"tag": "CLIENT_INTERNAL_ERROR"}}
                        error_response = Response(bot_timeout_json)
                        self.dispatch_error(error_response, ex)
                    except Exception as ex:
                        self.logger.error(ex, extra={"tag": "err"})
                        traceback.print_exc()

    def add_handler(self, handler):
        if isinstance(handler, Handler):
            if handler.is_default_handler():
                self.default_handler_object = handler
            else:
                self.message_handlers.append(handler)

    def add_handlers(self, handlers):
        if isinstance(handlers, list):
            for handler in handlers:
                self.add_handler(handler)
        else:
            self.add_handler(handlers)

    def remove_handler(self, handler):
        self.message_handlers.remove(handler)

    def add_error_handler(self, handler):
        self.error_handlers.append(handler)

    def add_error_handlers(self, handlers):
        if isinstance(handlers, list):
            self.error_handlers += handlers
        else:
            self.error_handlers.append(handlers)

    def remove_error_handler(self, handler):
        self.error_handlers.remove(handler)

    def dispatch_error(self, update, error):
        for error_handler in self.error_handlers:
            error_handler(self.bot, update, error)


    def message_handler(self, filters):
        def decorator(callback_func):
            handler = MessageHandler(filters, callback_func)
            self.add_handler(handler)

            return callback_func

        return decorator

    def command_handler(self, commands, include_template_response=False):
        def decorator(callback_func):
            handler = CommandHandler(commands, callback_func, include_template_response)
            self.add_handler(handler)

            return callback_func

        return decorator

    def default_handler(self):
        def decorator(callback_func):
            handler = MessageHandler(DefaultFilter(), callback_func)
            self.add_handler(handler)

            return callback_func

        return decorator

    def error_handler(self):
        def decorator(callback_func):
            self.add_error_handler(callback_func)

            return callback_func

        return decorator

    def register_conversation_next_step_handler(self, update, handlers):
        if isinstance(update, FatSeqUpdate) and update.is_message_update():

            next_step_handlers = []

            if isinstance(handlers, list):
                for handler in handlers:
                    if isinstance(handler, Handler):
                        next_step_handlers.append(handler)
            elif isinstance(handlers, Handler):
                next_step_handlers.append(handlers)

            user_peer = update.get_effective_user()
            user_id = user_peer.peer_id

            if user_id in self.conversation_next_step_handlers:
                self.conversation_next_step_handlers[user_id].clear()
                self.conversation_next_step_handlers[user_id] += next_step_handlers
            else:
                self.conversation_next_step_handlers[user_id] = next_step_handlers

    def conversation_finished(self, update):
        if isinstance(update, FatSeqUpdate) and update.is_message_update():
            user_peer = update.get_effective_user()
            user_id = user_peer.peer_id
            return user_id not in self.conversation_next_step_handlers and user_id not in self.conversation_data

    def finish_conversation(self, update):
        if isinstance(update, FatSeqUpdate) and update.is_message_update():
            user_peer = update.get_effective_user()
            user_id = user_peer.peer_id

            if user_id in self.conversation_next_step_handlers:
                self.conversation_next_step_handlers.pop(user_id)

            if user_id in self.conversation_data:
                self.conversation_data.pop(user_id)

    def set_conversation_data(self, update, key, value):
        if isinstance(update, FatSeqUpdate) and update.is_message_update():
            user_peer = update.get_effective_user()
            user_id = user_peer.peer_id

            if user_id in self.conversation_data:
                new_dict_element = {key: value}
                if isinstance(self.conversation_data[user_id], dict):
                    self.conversation_data[user_id].update(new_dict_element)
            else:
                self.conversation_data[user_id] = {key: value}

    def unset_conversation_data(self, update, key):
        if isinstance(update, FatSeqUpdate) and update.is_message_update():
            user_peer = update.get_effective_user()
            user_id = user_peer.peer_id

            if user_id in self.conversation_data:
                if isinstance(self.conversation_data[user_id], dict):
                    if key in self.conversation_data[user_id]:
                        del self.conversation_data[user_id][key]

    def clear_conversation_data(self, update):
        if isinstance(update, FatSeqUpdate) and update.is_message_update():
            user_peer = update.get_effective_user()
            user_id = user_peer.peer_id

            if user_id in self.conversation_data:
                if isinstance(self.conversation_data[user_id], dict):
                    self.conversation_data[user_id].clear()

    def get_conversation_data(self, update, key):
        if isinstance(update, FatSeqUpdate) and update.is_message_update():
            user_peer = update.get_effective_user()
            user_id = user_peer.peer_id

            if user_id in self.conversation_data:
                if isinstance(self.conversation_data[user_id], dict):
                    return self.conversation_data[user_id].get(key, None)
            else:
                return None

    # def get_difference_success_callback(self, response, user_data):
    #     if len(response.body.updates) > 0:
    #         for update in response.body.updates:
    #             self.process_fat_seq_update(update)
    #             self.last_seq = update.seq
    #             with open('last_seq.txt', 'w') as f:
    #                 f.write(str(self.last_seq))
    #     else:
    #         self.last_seq = response.body.seq
    #         with open('last_seq.txt', 'w') as f:
    #             f.write(str(self.last_seq))
    #     self.is_batch_updates_processed = True
    #     if response.body.need_more:
    #         self.get_updates()
    #     current_time = int(round(time.time() * 1000)) / 1000
    #     if current_time - self.last_poll_request_time >= self.timeInterval:
    #         self.poll()
    #     else:
    #         time.sleep(self.timeInterval - (current_time - self.last_poll_request_time))
    #         self.poll()

    # def get_difference_failure_callback(self, response, user_data):
    #     self.is_batch_updates_processed = True
    #     current_time = int(round(time.time() * 1000)) / 1000
    #     if current_time - self.last_poll_request_time >= self.timeInterval:
    #         self.poll()
    #     else:
    #         time.sleep(self.timeInterval - (current_time - self.last_poll_request_time))
    #         self.poll()

    # def get_updates(self):
    #     if self.is_batch_updates_processed:
    #         self.is_batch_updates_processed = False
    #         self.last_poll_request_time = int(round(time.time() * 1000)) / 1000
    #         self.bot.get_difference(self.last_seq, self.updates_number, self.get_difference_success_callback,
    #                                 self.get_difference_failure_callback)

    # def get_last_seq_success_callback(self, response, user_data):
    #     self.last_seq = response.body.seq
    #     with open('last_seq.txt', 'w') as f:
    #         f.write(str(self.last_seq))
    #     self.get_updates()

    # def get_last_seq(self):
    #     self.bot.get_last_seq(self.get_last_seq_success_callback)

    # def poll(self):
    #     if not self.real_time_fetch_updates:
    #         if self.continue_last_processed_seq:
    #             if self.last_seq:
    #                 self.get_updates()
    #             else:
    #                 if Path("last_seq.txt").exists():
    #                     with open('last_seq.txt', 'r') as f:
    #                         self.last_seq = int(f.readline())
    #                         self.get_updates()
    #                 else:
    #                     self.get_last_seq()
    #         else:
    #             self.get_last_seq()
