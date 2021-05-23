import logging
import logging.config

from ..config import Config

logging.config.dictConfig(Config.LOGGING_CONFIG)
main_logger = logging.getLogger('Websocket')
main_logger.setLevel(Config.LOG_LEVEL)
