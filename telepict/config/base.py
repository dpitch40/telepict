import os

class Config:
    DB_URL = None
    HTTP_PORT = int(os.environ['FLASK_RUN_PORT'])
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
