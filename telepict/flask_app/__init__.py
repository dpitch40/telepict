import os.path
import logging
import logging.config
import logging.handlers

from flask import Flask, request, flash, redirect, url_for

from ..config import Config
from ..config.logging_config import update_werkzeug_logger
from .auth import bp as auth_bp
from .game import bp as game_bp
from .image import bp as image_bp
from ..db import DB
from .exceptions import FlashedError

app_dir = os.path.dirname(os.path.dirname(__file__))

logging.config.dictConfig(Config.LOGGING_CONFIG)

# import logging_tree
# logging_tree.printout()

app = Flask('Telepict', template_folder=os.path.join(app_dir, 'templates'),
            static_folder=os.path.join(app_dir, 'static'))
app.jinja_env.add_extension('jinja2.ext.do')
app.config.from_object(Config)
app.db = DB()

update_werkzeug_logger()

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
