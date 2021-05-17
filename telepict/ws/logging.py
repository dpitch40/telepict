import logging
import logging.config

from ..config import Config

logging.config.dictConfig(Config.LOGGING_CONFIG)
logger = logging.getLogger('Websocket')
