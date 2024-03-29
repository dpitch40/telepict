import os.path
import logging
import logging.config
import logging.handlers
from urllib.parse import urlparse
import base64

import pytz
from flask import Flask, request, flash, redirect, url_for, session

from ..config import Config
from ..config.logging_config import update_werkzeug_logger
from .auth import bp as auth_bp
from .game import bp as game_bp
from .image import bp as image_bp
from ..db import DB
from .exceptions import FlashedError
from .util import get_current_player

app_dir = os.path.dirname(os.path.dirname(__file__))

logging.config.dictConfig(Config.LOGGING_CONFIG)

app = Flask('Telepict', template_folder=os.path.join(app_dir, 'templates'),
            static_folder=os.path.join(app_dir, 'static'))
app.jinja_env.add_extension('jinja2.ext.do')
# Load secret key if enabled
secret_key_message = None
if Config.SECRET_KEY_FILE is not None and os.path.isfile(Config.SECRET_KEY_FILE):
    secret_key_message = f'Loading secret key from {Config.SECRET_KEY_FILE}'
    Config.SECRET_KEY = open(Config.SECRET_KEY_FILE, 'rb').read()
encryption_key_message = None
if Config.ENCRYPTION_KEY_FILE is not None and os.path.isfile(Config.ENCRYPTION_KEY_FILE):
    encryption_key_message = f'Loading encryption key from {Config.ENCRYPTION_KEY_FILE}'
    Config.ENCRYPTION_KEY = base64.b64encode(open(Config.ENCRYPTION_KEY_FILE, 'rb').read())
else:
    encryption_key_message = f'WARNING: Using Flask secret key for encryption key'
    Config.ENCRYPTION_KEY = base64.b64encode(Config.SECRET_KEY[:32])

app.config.from_object(Config)
app.db = DB()

app.logger.info('Started app (%s)', app.config['TELEPICT_ENV'])
if secret_key_message:
    app.logger.info(secret_key_message)
if encryption_key_message:
    app.logger.info(encryption_key_message)

# Initialize image backend
image_backend = app.config['IMAGE_BACKEND'].get_instance(**app.config['IMAGE_BACKEND_KWARGS'])

# import logging_tree
# logging_tree.printout()

update_werkzeug_logger()

app.register_blueprint(auth_bp)
app.register_blueprint(game_bp)
app.register_blueprint(image_bp)

@app.before_request
def check_for_access_code():
    if 'code' in request.args:
        session['access_code'] = request.args['code']

@app.template_filter('render_timestamp')
def render_timestamp_filter(ts):
    with app.db.session_scope() as session:
        player = get_current_player(session)
        if not player:
            tz = 'UTC'
        else:
            tz = player.timezone
        utc_timestamp = ts.replace(tzinfo=pytz.utc)
        local_timestamp = utc_timestamp.astimezone(pytz.timezone(tz))
        return local_timestamp.strftime(Config.TS_FORMAT)

@app.context_processor
def inject_external_url():
    if not hasattr(app, 'server_full'):
        url = url_for('game.index', _external=True)
        app.logger.info('External url: %s', url)
        scheme, loc, path, _, _, _ = urlparse(url)
        app.server = loc
        app.server_name = loc.split(':', 1)[0]
        app.server_full = scheme + '://' + loc
    return {'server': app.server,
            'server_name': app.server_name,
            'server_full': app.server_full}

@app.errorhandler(FlashedError)
def handle_flashed_error(exc):
    flash(exc.message, exc.category)
    if exc.redirect:
        return redirect(exc.redirect, 303)
    else:
        return redirect(request.url, 303)
