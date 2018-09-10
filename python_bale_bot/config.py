import logging
import os


class Config:
    # bot config
    base_url = os.environ.get('BASE_URL', "https://apitest.bale.ai/v1/bots/http")
    request_timeout = int(os.environ.get('REQUEST_TIMEOUT', 5))
    # logging config
    # 0:print to output        1:use graylog       2:both 0 and 1
    use_graylog = os.environ.get('SDK_USE_GRAYLOG', "0")
    source = os.environ.get('LOG_SOURCE', "bot_source")
    graylog_host = os.environ.get('SDK_GRAYLOG_HOST', "172.30.41.67")
    graylog_port = int(os.environ.get('SDK_GRAYLOG_PORT', 12201))
    log_level = int(os.environ.get('SDK_LOG_LEVEL', logging.DEBUG))
    log_facility_name = os.environ.get('SDK_LOG_FACILITY_NAME', "python_bale_bot")
    monitoring_hash = os.environ.get('MONITORING_HASH', "SADJSDSDas4d2asf41f2a2faasd45sas-")
    # updater config
    default_worker_numbers = int(os.environ.get('WORKERS', 64))
    # webhook config
    webhook_listen_address = os.environ.get("WEBHOOK_LISTEN_ADDRESS", "0.0.0.0")
    webhook_listen_port = int(os.environ.get("WEBHOOK_LISTEN_PORT", 8027))
    # requests session and adapter config
    default_adapter_pool_connections = int(os.environ.get('ADAPTER_POOL_CONNECTIONS', 2))
    default_pool_maxsize = int(os.environ.get('POOL_MAX_SIZE', 20))

    # polling config
    # real_time_fetch_updates = os.environ.get('REAL_TIME_FETCH_UPDATES', True)
    # continue_last_processed_seq = os.environ.get('CONTINUE_LAST_PROCESSED_SEQ', False)
    # timeInterval = int(os.environ.get('TIME_INTERVAL', 1))# unit for time interval is second)
    # updates_number = int(os.environ.get('UPDATES_NUMBER', 3))
