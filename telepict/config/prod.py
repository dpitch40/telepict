import os
import logging

from .base import Config, make_logging_config
from ..util.image.s3_based import S3ImageBackend

class ConfigProd(Config):
    DBFILE = os.path.expanduser(os.path.join('~', '.telepict', 'telepict.db'))
    DB_URL = f"sqlite:///{DBFILE}"
    ACCESS_CODE_FILE = '/tmp/telepict_access_code'
    REQUIRE_ACCESS_CODE = True
    SECRET_KEY_FILE = '/home/ec2-user/.secret_key'
    LOG_LEVEL = logging.INFO
    LOGGING_CONFIG = make_logging_config(LOG_LEVEL, os.getenv('LOG_DIR'))
    IMAGE_BACKEND = S3ImageBackend
    IMAGE_BACKEND_KWARGS = {'bucket': 'telepict-images'}
