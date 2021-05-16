from .base import Config, LoggingConfig

class ConfigTest(Config):
    DB_URL = "sqlite://"
    TESTING = True
    SECRET_KEY = 'test_secret_key'
    HASH_ITERATIONS = 1000

class LoggingConfigTest(LoggingConfig):
    pass
