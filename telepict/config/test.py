import logging

from .base import Config, make_logging_config

class ConfigTest(Config):
    LOG_LEVEL = logging.DEBUG
    DB_URL = "sqlite://"
    TESTING = True
    SECRET_KEY = 'test_secret_key'
    HASH_ITERATIONS = 1000
    LOGGING_CONFIG = make_logging_config(LOG_LEVEL)
