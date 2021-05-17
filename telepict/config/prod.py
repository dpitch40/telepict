import os
import logging

from .base import Config, make_logging_config

class ConfigProd(Config):
    LOG_LEVEL = logging.INFO
    LOGGING_CONFIG = make_logging_config(LOG_LEVEL, os.getenv('LOG_DIR'))
