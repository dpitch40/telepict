import os
import logging

from .base import Config, LoggingConfig

LOG_LEVEL = logging.DEBUG

class ConfigDev(Config):
    DBFILE = 'telepict.db'
    DB_URL = f"sqlite:///{DBFILE}"

    SECRET_KEY = 'secret_key'

class LoggingConfigDev(LoggingConfig):
    pass

LoggingConfigDev.handlers['stream']['level'] = LOG_LEVEL
LoggingConfigDev.root['level'] = LOG_LEVEL

if 'LOG_DIR' in os.environ:
    LoggingConfigDev.setup_logfile(os.environ['LOG_DIR'], LOG_LEVEL)
