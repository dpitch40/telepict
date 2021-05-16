import logging

from ..config import LoggingConfig
from ..util import configure_logging

configure_logging(LoggingConfig)
logger = logging.getLogger('Websocket')
