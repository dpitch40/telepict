import os

from .base import Config, LoggingConfig

class ConfigDev(Config):
    DBFILE = 'telepict.db'
    DB_URL = f"sqlite:///{DBFILE}"

    SECRET_KEY = 'secret_key'

class LoggingConfigDev(LoggingConfig):
    pass

if 'LOGFILE' in os.environ:
    LoggingConfigDev.setup_logfile(os.environ['LOGFILE'])
