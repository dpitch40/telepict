from config.base import Config

class ConfigTest(Config):
    DB_URL = "sqlite://"
    TESTING = True
