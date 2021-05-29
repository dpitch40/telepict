import os
import logging

from .base import Config, make_logging_config

class ConfigDev(Config):
    ENV ='dev'
    LOG_LEVEL = logging.DEBUG
    DEBUG = True
    DBFILE = 'telepict.db'
    DB_URL = f"sqlite:///{DBFILE}"
    LOGGING_CONFIG = make_logging_config(LOG_LEVEL, os.getenv('LOG_DIR'))
