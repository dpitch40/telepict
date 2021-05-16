import os
import os.path
import logging

LOG_LEVEL = logging.INFO

class Config:
    DB_URL = None
    HTTP_PORT = int(os.environ.get('FLASK_RUN_PORT', 8764))
    WS_PORT = 8765
    SECRET_KEY = None
    HASH_ITERATIONS = 500000

    MAX_IMAGE_WIDTH = 1080
    MAX_IMAGE_HEIGHT = 700
    CANVAS_WIDTH = 640
    CANVAS_HEIGHT = 414
    JPEG_QUALITY = 80
    MAX_WS_MESSAGE_SIZE = 2 ** 21

    TS_FORMAT = "%b %d, %Y, %H:%M"



class LoggingConfig:
    version = 1
    disable_existing_loggers = False
    formatters = {
        'default': {
            'format': '%(asctime)s %(name)s %(pathname)s.%(lineno)d %(levelname)s: %(message)s'
        }
    }
    handlers = {
        'stream': {
            'class': 'logging.StreamHandler',
            'level': LOG_LEVEL,
            'formatter': 'default',
            'stream': 'ext://sys.stdout'
        }
    }
    root = {
        'level': LOG_LEVEL,
        'handlers': ['stream']
    }

    @classmethod
    def setup_logfile(cls, logfile):
        cls.handlers['file'] = {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': LOG_LEVEL,
            'formatter': 'default',
            'filename': logfile,
            'maxBytes': 2 ** 20,
            'backupCount': 10,
        }
        cls.root['handlers'].append('file')
