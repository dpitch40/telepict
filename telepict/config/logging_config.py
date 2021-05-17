import re
import os
import os.path

import logging
import logging.handlers
from . import Config

get_resource_re = re.compile(r'GET\s+([^\s]+) HTTP')
ignore_uri_re = re.compile(r'(?:min\.(?:js|css)|\.ico)', flags=re.I)

def filter_werkzeug_access(record):
    # Ignores access messages for common/trivial resources
    if record.args:
        m = get_resource_re.search(record.args[0])
        if m and ignore_uri_re.search(m.group(1)):
            return False
    return True

def update_werkzeug_logger():
    werkzeug_logger = logging.getLogger('werkzeug')
    # Prevent the werkzeug logger from propagating to root
    werkzeug_logger.propagate = False
    # Add filter
    werkzeug_logger.addFilter(filter_werkzeug_access)
    # Set up rotating file handler for access log
    if 'LOG_DIR' in os.environ and werkzeug_logger.handlers:
        werkzeug_handler = werkzeug_logger.handlers[0]
        access_handler = logging.handlers.RotatingFileHandler(
            os.path.join(os.environ['LOG_DIR'], 'flask-access.log'),
            maxBytes=2**20, backupCount=10)
        access_handler.setLevel(Config.LOG_LEVEL)
        access_handler.setFormatter(werkzeug_handler.formatter)
        werkzeug_logger.addHandler(access_handler)
