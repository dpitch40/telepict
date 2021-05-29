import os
import os.path
import logging

from ..util.image.file_based import FileImageBackend

logging.getLogger('websockets').setLevel(logging.INFO)

LOG_LEVEL = logging.INFO

class Config:
    DB_URL = None
    HTTP_PORT = int(os.environ.get('FLASK_RUN_PORT', 8764))
    WS_PROTOCOL = 'ws'
    WS_HOST = '0.0.0.0'
    WS_PORT = 8001
    EXTERNAL_WS_PORT = WS_PORT
    WS_CERTFILE = None
    WS_KEYFILE = None
    SECRET_KEY = b'\xdfH~{S\t\xe9\xec*`\xe6Cr\xbe\x06*\xcc3\x7f\xea\xef\xee\xb9\xc5\xad*\x96\xc9\xcd\x15\x05\x16\xf7\x92*<\x99n\x86\xcecd"]z\x89\x9br\x94\x07\xef\xee\xcf\xdc\x1a?,9\x88\xdb\xd5Lk1'
    SECRET_KEY_FILE = None
    ENCRYPTION_KEY = None
    ENCRYPTION_KEY_FILE = None
    HASH_ITERATIONS = 500000
    ACCESS_CODE_FILE = 'access_codes'
    REQUIRE_ACCESS_CODE = False
    MAX_ACCESS_CODE_AGE = 3600

    MAX_IMAGE_WIDTH = 1080
    MAX_IMAGE_HEIGHT = 700
    CANVAS_WIDTH = 640
    CANVAS_HEIGHT = 414
    JPEG_QUALITY = 80
    MAX_WS_MESSAGE_SIZE = 2 ** 21
    IMAGE_BACKEND = FileImageBackend
    IMAGE_BACKEND_KWARGS = {}

    TS_FORMAT = "%b %d, %Y, %H:%M"

def make_logging_config(level, log_dir=None):
    config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'default': {
                'format': '%(asctime)s %(levelname)s %(name)s[%(process)s] %(pathname)s.%(lineno)d: %(message)s'
            }
        },
        'handlers': {
            'stream': {
                'class': 'logging.StreamHandler',
                'level': level,
                'formatter': 'default',
                'stream': 'ext://sys.stdout'
            }
        },
        'loggers': {
            'Telepict': {
                'level': level,
                'propagate': False,
                'handlers': ['stream']
            }
        },
        'root': {
            'level': logging.INFO,
            'handlers': ['stream']
        }
    }
    if log_dir is not None:
        config['handlers']['file'] = {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': level,
            'formatter': 'default',
            'filename': os.path.join(log_dir, 'telepict.log'),
            'maxBytes': 2 ** 20,
            'backupCount': 10,
        }
        config['root']['handlers'].append('file')
        config['loggers']['Telepict']['handlers'].append('file')
    return config
