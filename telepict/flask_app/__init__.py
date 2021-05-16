import io
import os
import re
import os.path
import logging
import logging.config
import logging.handlers

from flask import Flask, render_template, request, flash, redirect, session as flask_session, \
    current_app, url_for, jsonify
from PIL import Image
import logging_tree

from ..config import Config, LoggingConfig, LOG_LEVEL
from .auth import bp as auth_bp, require_logged_in
from .game import bp as game_bp
from .image import bp as image_bp
from ..db import DB, Player, Game, PendingGame, PendingGamePlayerAssn, Invitation, Stack, Drawing
from .exceptions import FlashedError
from ..util import get_pending_stacks, configure_logging
from ..util.image import flatten_rgba_image
from .util import inject_current_player

get_resource_re = re.compile(r'GET\s+([^\s]+) HTTP')
ignore_uri_re = re.compile(r'min\.(js|css)', flags=re.I)

app_dir = os.path.dirname(os.path.dirname(__file__))

configure_logging(LoggingConfig)
# import logging_tree
# logging_tree.printout()

app = Flask('Telepict', template_folder=os.path.join(app_dir, 'templates'),
            static_folder=os.path.join(app_dir, 'static'))
app.jinja_env.add_extension('jinja2.ext.do')
app.config.from_object(Config)
app.db = DB()

def filter_werkzeug_access(record):
    if record.args:
        m = get_resource_re.search(record.args[0])
        if m and ignore_uri_re.search(m.group(1)):
            return False
    return True

# Redirect the werkzeug logger
werkzeug_logger = logging.getLogger('werkzeug')
werkzeug_logger.propagate = False
werkzeug_logger.addFilter(filter_werkzeug_access)
if 'LOG_DIR' in os.environ and werkzeug_logger.handlers:
    werkzeug_handler = werkzeug_logger.handlers[0]
    access_handler = logging.handlers.RotatingFileHandler(
        os.path.join(os.environ['LOG_DIR'], 'flask-access.log'),
        maxBytes=2**20, backupCount=10)
    access_handler.setLevel(LOG_LEVEL)
    access_handler.setFormatter(werkzeug_handler.formatter)
    werkzeug_logger.addHandler(access_handler)

app.register_blueprint(auth_bp)
app.register_blueprint(game_bp)
app.register_blueprint(image_bp)

@app.context_processor
def inject_external_url():
    pre_port_url = url_for('game.index', _external=True).rsplit(':', 1)[0]
    # Strip protocol off
    server = pre_port_url.split(':', 1)[1].lstrip('/')
    return {'server': server}

@app.errorhandler(FlashedError)
def handle_flashed_error(exc):
    flash(exc.message, exc.category)
    return redirect(request.url, 303)
