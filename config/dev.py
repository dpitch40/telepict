from config.base import Config

class ConfigDev(Config):
    DBFILE = 'telepict.db'
    DB_URL = f"sqlite:///{DBFILE}"

    SECRET_KEY = 'secret_key'
