import traceback
from queue import Queue
from threading import Event, Lock, Thread, current_thread
from time import sleep
import requests
from requests.adapters import HTTPAdapter
from python_bale_bot.dispatcher import Dispatcher
from python_bale_bot.error import *
from python_bale_bot.utils.logger import Logger
from python_bale_bot.config import Config
from python_bale_bot.bot import Bot
from python_bale_bot.utils.webhookhandler import WebhookServer, WebhookHandler


class Updater:
    _session = None

    def __init__(self, token, user_id, base_url=None, workers=Config.default_worker_numbers, bot=None,
                 adapter_kwargs=None):

        self.logger = Logger.get_logger()

        if not token:
            raise ValueError("`token` did't passed")

        if (token is None) and (bot is None):
            raise ValueError('`token` or `bot` must be passed')

        if not user_id:
            raise ValueError("`user_id` did't passed")

        con_pool_size = workers + 4
        if bot is not None:
            # T ODO bot.adapter.pool_connections * bot.adapter.pool_maxsize or bot.adapter.pool_maxsize
            max_available_conn = bot.adapter.pool_maxsize
            self.bot = bot
            if con_pool_size > max_available_conn:
                self.logger.warning(
                    'Connection pool of Adapter object is smaller than optimal value (%s)',
                    con_pool_size)
        else:
            # we need a connection pool the size of:
            # * for each of the workers
            # * 1 for Dispatcher
            # * 1 for polling Updater (even if webhook is used, we can spare a connection)
            # * 1 for JobQueue
            # * 1 for main thread
            if adapter_kwargs is None:
                adapter_kwargs = {}

            if 'pool_connections' not in adapter_kwargs:
                adapter_kwargs['pool_connections'] = Config.default_adapter_pool_connections
            if 'pool_maxsize' not in adapter_kwargs:
                adapter_kwargs['pool_maxsize'] = Config.default_pool_maxsize
            self.adapter = HTTPAdapter(**adapter_kwargs)
            self.session = requests.Session()
            self.bot = Bot(token, user_id, base_url, adapter=self.adapter, session=self.session)
        self.incoming_queue = Queue()
        self.__exception_event = Event()
        self.dispatcher = Dispatcher(
            self.bot,
            self.incoming_queue,
            workers=workers,
            exception_event=self.__exception_event)

        self.token = token
        self.timeout = Config.request_timeout
        self.last_update_id = 0
        self.running = False
        self.is_idle = False
        self.httpd = None
        self.__lock = Lock()
        self.__threads = []

        # self.bale_futures = []

    def _init_thread(self, target, name, *args, **kwargs):
        thr = Thread(target=self._thread_wrapper, name=name, args=(target,) + args, kwargs=kwargs)
        thr.start()
        self.__threads.append(thr)

    def _thread_wrapper(self, target, *args, **kwargs):
        thr_name = current_thread().name
        self.logger.debug('thread {0}  started'.format(thr_name))
        try:
            target(*args, **kwargs)
        except Exception as ex:
            self.logger.error(ex, extra={"tag": "err"})
            self.__exception_event.set()
            self.logger.exception('unhandled exception in thread %s', thr_name)
            traceback.print_exc()
            raise
        self.logger.debug('thread {0} - ended'.format(thr_name))

    # TODO should implement polling behavior of updater after server api is ready
    # def start_polling(self,
    #                   poll_interval=0.0,
    #                   timeout=10,
    #                   clean=False,
    #                   bootstrap_retries=-1,
    #                   read_latency=2.,
    #                   allowed_updates=None):
    #     with self.__lock:
    #         if not self.running:
    #             self.running = True
    #
    #             # Create & start threads
    #             # self.job_queue.start()#--------------------
    #             dispatcher_ready = Event()
    #             # self._init_thread(self.dispatcher.start, "dispatcher", ready=dispatcher_ready)
    #             self._init_thread(self._start_polling, "updater", poll_interval, timeout,
    #                               read_latency, bootstrap_retries, clean, allowed_updates)
    #
    #             dispatcher_ready.wait()
    #
    #             # Return the update queue so the main thread can insert updates
    #             return self.incoming_queue

    # def _start_polling(self, poll_interval, timeout, read_latency, bootstrap_retries, clean,
    #                    allowed_updates):  # pragma: no cover
    #     # Thread target of thread 'updater'. Runs in background, pulls
    #     # updates from Telegram and inserts them in the update queue of the
    #     # Dispatcher.
    #
    #     self.logger.debug('Updater thread started (polling)')
    #
    #     self._bootstrap(bootstrap_retries, clean=clean, webhook_url='', allowed_updates=None)  # ???
    #
    #     self.logger.debug('Bootstrap done')
    #
    #     def polling_action_cb():
    #         updates = self.bot.get_difference(
    #             self.last_update_id, timeout=timeout, read_latency=read_latency,
    #             allowed_updates=allowed_updates)
    #
    #         if updates:
    #             if not self.running:
    #                 self.logger.debug('Updates ignored and will be pulled again on restart')
    #             else:
    #                 for update in updates:
    #                     self.incoming_queue.put(update)
    #                 self.last_update_id = updates[-1].update_id + 1
    #
    #         return True
    #
    #     def polling_onerr_cb(exc):
    #         # Put the error into the update queue and let the Dispatcher
    #         # broadcast it
    #         self.incoming_queue.put(exc)
    #
    #     self._network_loop_retry(polling_action_cb, polling_onerr_cb, 'getting Updates',
    #                              poll_interval)
    def start_webhook(self,
                      listen=Config.webhook_listen_address,
                      port=Config.webhook_listen_port,
                      url_path='',
                      cert=None,
                      key=None,
                      clean=False,
                      bootstrap_retries=0,
                      webhook_url=None):
        with self.__lock:
            if not self.running:
                self.running = True

                # Create & start threads
                # self.job_queue.start()
                self._init_thread(self.dispatcher.start, "dispatcher"),
                self._init_thread(self._start_webhook, "updater", listen, port, url_path, cert,
                                  key, bootstrap_retries, clean, webhook_url)

                # Return the update queue so the main thread can insert updates
                return self.incoming_queue

    def _start_webhook(self, listen, port, url_path, cert, key, bootstrap_retries, clean, webhook_url):
        self.logger.debug('Updater thread started (webhook)')
        # use_ssl = cert is not None and key is not None
        if not url_path.startswith('/'):
            url_path = '/{0}'.format(url_path)

        # Create and start server
        self.httpd = WebhookServer((listen, port), WebhookHandler, self.incoming_queue, url_path, self.bot)

        # if use_ssl:
        #     self._check_ssl_cert(cert, key)
        #
        #     # DO NOT CHANGE: Only set webhook if SSL is handled by library
        if not webhook_url:
            webhook_url = self._gen_webhook_url(listen, port, url_path)
        # self._bootstrap(max_retries=bootstrap_retries, clean=clean, webhook_url=webhook_url)
        # elif clean:
        #     self.logger.warning("cleaning updates is not supported if "
        #                         "SSL-termination happens elsewhere; skipping")

        self.httpd.serve_forever(poll_interval=1)

    # def _check_ssl_cert(self, cert, key):
    #     # Check SSL-Certificate with openssl, if possible
    #     try:
    #         exit_code = subprocess.call(
    #             ["openssl", "x509", "-text", "-noout", "-in", cert],
    #             stdout=open(os.devnull, 'wb'),
    #             stderr=subprocess.STDOUT)
    #     except OSError:
    #         exit_code = 0
    #     if exit_code is 0:
    #         try:
    #             self.httpd.socket = ssl.wrap_socket(
    #                 self.httpd.socket, certfile=cert, keyfile=key, server_side=True)
    #         except ssl.SSLError as error:
    #             self.logger.exception('Failed to init SSL socket')
    #             raise TelegramError(str(error))
    #     else:
    #         raise TelegramError('SSL Certificate invalid')
    def _network_loop_retry(self, action_cb, onerr_cb, description, interval):
        self.logger.debug('Start network loop retry %s', description)
        cur_interval = interval
        while self.running:
            try:
                if not action_cb():
                    break
            except Exception as e:
                print(e)
            except RetryAfter as e:
                self.logger.info('%s', e)
                cur_interval = 0.5 + e.retry_after
            except TimedOut as toe:
                self.logger.debug('Timed out %s: %s', description, toe)
                # If failure is due to timeout, we should retry asap.
                cur_interval = 0
            except InvalidToken as pex:
                self.logger.error('Invalid token; aborting')
                raise pex
            except BaleError as te:
                self.logger.error('Error while %s: %s', description, te)
                onerr_cb(te)
                cur_interval = self._increase_poll_interval(cur_interval)
            else:
                cur_interval = interval

            if cur_interval:
                sleep(cur_interval)

    @staticmethod
    def _gen_secure_webhook_url(listen, port, url_path):
        return 'https://{listen}:{port}{path}'.format(listen=listen, port=port, path=url_path)

    @staticmethod
    def _gen_webhook_url(listen, port, url_path):
        return 'http://{listen}:{port}{path}'.format(listen=listen, port=port, path=url_path)

    # TODO bootstrap issues must be fixed
    def _bootstrap(self, max_retries, clean, webhook_url, cert=None, bootstrap_interval=5):
        retries = [0]

        def bootstrap_del_webhook():
            self.bot.delete_webhook()
            return False

        def bootstrap_clean_updates():
            self.logger.debug('Cleaning updates from Bale server')
            updates = self.bot.get_difference()
            while updates:
                updates = self.bot.get_difference(updates[-1].update_id + 1)
            return False

        def bootstrap_set_webhook():
            self.bot.set_webhook(end_point=webhook_url)
            return False

        def bootstrap_onerr_cb(exc):
            if not isinstance(exc, Unauthorized) and (max_retries < 0 or retries[0] < max_retries):
                retries[0] += 1
                self.logger.warning('Failed bootstrap phase; try=%s max_retries=%s',
                                    retries[0], max_retries)
            else:
                self.logger.error('Failed bootstrap phase after %s retries (%s)', retries[0], exc)
                raise exc

        # Cleaning pending messages is done by polling for them - so we need to delete webhook if
        # one is configured.
        # We also take this chance to delete pre-configured webhook if this is a polling Updater.
        # NOTE: We don't know ahead if a webhook is configured, so we just delete.

        if clean or not webhook_url:
            self._network_loop_retry(bootstrap_del_webhook, bootstrap_onerr_cb,
                                     'bootstrap del webhook', bootstrap_interval)
            retries[0] = 0
        # Clean pending messages, if requested.
        if clean:
            self._network_loop_retry(bootstrap_clean_updates, bootstrap_onerr_cb,
                                     'bootstrap clean updates', bootstrap_interval)
            retries[0] = 0
            sleep(1)

        # Restore/set webhook settings, if needed. Again, we don't know ahead if a webhook is set,
        # so we set it anyhow.
        if webhook_url:
            self._network_loop_retry(bootstrap_set_webhook, bootstrap_onerr_cb,
                                     'bootstrap set webhook', bootstrap_interval)

    @staticmethod
    def _increase_poll_interval(current_interval):
        # increase waiting times on subsequent errors up to 30secs
        if current_interval == 0:
            current_interval = 1
        elif current_interval < 30:
            current_interval += current_interval / 2
        elif current_interval > 30:
            current_interval = 30
        return current_interval

    def stop(self):
        """Stops the polling/webhook thread, the dispatcher and the job queue."""

        # self.job_queue.stop()
        with self.__lock:
            if self.running or self.dispatcher.has_running_threads:
                self.logger.debug('Stopping Updater and Dispatcher...')

                self.running = False

                # self._stop_httpd()
                self._stop_dispatcher()
                self._join_threads()

                # Stop the Session instance only if it was created by the Updater
                if self.session:
                    self.session.close()

    def _stop_httpd(self):
        if self.httpd:
            self.logger.debug('Waiting for current webhook connection to be closed...')
            self.httpd.shutdown()
            self.httpd = None

    def _stop_dispatcher(self):
        self.logger.debug('Requesting Dispatcher to stop...')
        self.dispatcher.stop()

    def _join_threads(self):
        for thr in self.__threads:
            self.logger.debug('Waiting for {0} thread to end'.format(thr.name))
            thr.join()
            self.logger.debug(' thread {0}  has been ended'.format(thr.name))
        self.__threads = []
