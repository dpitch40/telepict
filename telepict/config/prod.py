import os
import logging

from .base import Config, make_logging_config
from ..util.image.s3_based import S3ImageBackend

class ConfigProd(Config):
    ACCESS_CODE_FILE = '/tmp/telepict_access_code'
    REQUIRE_ACCESS_CODE = True
    LOG_LEVEL = logging.INFO
    LOGGING_CONFIG = make_logging_config(LOG_LEVEL, os.getenv('LOG_DIR'))
    IMAGE_BACKEND = S3ImageBackend
