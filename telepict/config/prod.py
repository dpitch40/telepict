import os
import os.path
import logging

from .base import Config, make_logging_config
from ..util.image.s3_based import S3ImageBackend

class ConfigProd(Config):
    DBFILE = os.path.join('/var', 'db', 'telepict', 'telepict.db')
    # WS_CERTFILE = '/etc/letsencrypt/live/www.telephone-pictionary.net/fullchain.pem'
    # WS_KEYFILE = '/etc/letsencrypt/live/www.telephone-pictionary.net/privkey.pem'
    WS_PROTOCOL = 'wss'
    EXTERNAL_WS_PORT = 8002
    DB_URL = f"sqlite:///{DBFILE}"
    ACCESS_CODE_FILE = '/home/ec2-user/.telepict/telepict_access_codes'
    REQUIRE_ACCESS_CODE = True
    SECRET_KEY = None
    SECRET_KEY_FILE = '/home/ec2-user/.telepict/.secret_key'
    ENCRYPTION_KEY_FILE = '/home/ec2-user/.telepict/.encryption_key'
    LOG_LEVEL = os.getenv('LOG_LEVEL', logging.INFO)
    LOGGING_CONFIG = make_logging_config(LOG_LEVEL, os.getenv('LOG_DIR'))
    IMAGE_BACKEND = S3ImageBackend
    IMAGE_BACKEND_KWARGS = {'bucket': 'telepict-images'}
