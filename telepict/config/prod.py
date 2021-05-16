import os
import logging

from .base import Config, LoggingConfig

LOG_LEVEL = logging.INFO

class ConfigProd(Config):
    DB_URL = None

class LoggingConfigProd(LoggingConfig):
    pass

if 'LOGFILE' in os.environ:
    LoggingConfigProd.setup_logfile(os.environ['LOGFILE'])
