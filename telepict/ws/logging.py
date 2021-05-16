import logging

from ..config import Config, LoggingConfig
from ..util import configure_logging

configure_logging(LoggingConfig)
logger = logging.getLogger('Websocket')
