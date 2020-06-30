from config.base import Config

class ConfigTest(Config):
    DB_URL = "sqlite://"
    TESTING = True
    SECRET_KEY = 'test_secret_key'
    HASH_ITERATIONS = 1000
