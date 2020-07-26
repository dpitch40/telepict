import io
import os.path

from flask import Flask, render_template, request, flash, redirect, session as flask_session, \
    current_app, url_for, jsonify
from PIL import Image

from ..config import Config
from .auth import bp as auth_bp, require_logged_in
from .game import bp as pending_bp
from ..db import DB, Player, Game, PendingGame, PendingGamePlayerAssn, Invitation, Stack, Drawing
from .exceptions import FlashedError
from ..util import get_pending_stacks
from ..util.image import flatten_rgba_image
from .util import inject_current_player

app_dir = os.path.dirname(os.path.dirname(__file__))

app = Flask('Telepict', template_folder=os.path.join(app_dir, 'templates'),
            static_folder=os.path.join(app_dir, 'static'))
app.jinja_options['extensions'].append('jinja2.ext.do')
app.config.from_object(Config)
app.db = DB()

app.register_blueprint(auth_bp)
app.register_blueprint(pending_bp)

@app.route('/img_upload', methods=['POST'])
def image_upload():
    game_id = int(request.form['game_id'])
    player_id = int(request.form['player_id'])

    with current_app.db.session_scope() as session:
        game = session.query(Game).get(game_id)
        player = session.query(Player).get(player_id)
        pending_stacks = get_pending_stacks(game, player)

        if pending_stacks:
            stack = pending_stacks[0]
            if isinstance(stack.last, Drawing):
                current_app.logger.error('%s trying to add a drawing to stack %d when '
                                         'it already ended with a drawing', player.name, stack.id_)
            else:
                f = request.files['file']
                image = Image.open(f)
                if image.mode == 'RGBA':
                    image = flatten_rgba_image(image)
                # Scale image if necessary
                width_factor = image.size[0] / current_app.config['MAX_IMAGE_WIDTH']
                height_factor = image.size[1] / current_app.config['MAX_IMAGE_HEIGHT']
                max_factor = max(height_factor, width_factor)
                if max_factor > 1:
                    target_size = (int(image.size[0] // max_factor),
                                   int(image.size[1] // max_factor))
                    image = image.resize(target_size)

                bio = io.BytesIO()
                image.save(bio, format='JPEG', quality=Config.JPEG_QUALITY)

                drawings = Drawing(author=player, stack=stack, drawing=bio.getvalue())
                stack.drawings.append(drawings)
                session.add(drawings)
                session.commit()
        else:
            current_app.logger.error('%s trying to add a drawing with no pending stacks',
                                     player.name)

    return jsonify({})



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
