import os

from .base import Config, LoggingConfig

class ConfigProd(Config):
    DB_URL = None

class LoggingConfigProd(LoggingConfig):
    pass

if 'LOGFILE' in os.environ:
    LoggingConfigProd.setup_logfile(os.environ['LOGFILE'])
