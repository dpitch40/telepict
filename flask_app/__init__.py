import io

from flask import Flask, render_template, request, flash, redirect, session as flask_session, \
    current_app, url_for, jsonify
from PIL import Image

from config import Config
from .auth import bp as auth_bp, require_logged_in
from .pending import bp as pending_bp
from db import DB, Player, Game, PendingGame, PendingGamePlayerAssn, Invitation, Stack, Drawing
from .exceptions import FlashedError
from util import get_pending_stacks
from util.image import flatten_rgba_image
from .util import inject_current_player

app = Flask('Telepict')
app.config.from_object(Config)
app.db = DB()

app.register_blueprint(auth_bp)
app.register_blueprint(pending_bp)

@app.route('/')
def index():
    if 'username' in flask_session:
        view_data = dict()
        with current_app.db.session_scope() as session:
            player = session.query(Player).filter_by(name=flask_session['username']).one_or_none()
            if player:
                view_data['games'] = player.games
                view_data['pending_games'] = player.pending_games
                view_data['player'] = player
                view_data['invitations'] = player.invitations
                return render_template('index.html', **view_data)

    return render_template('index.html')

@app.route('/game/<int:game_id>')
@inject_current_player
@require_logged_in
def view_game(session, current_player, game_id):
    with current_app.db.session_scope() as session:
        game = session.query(Game).get(game_id)
        if game is None:
            raise FlashedError('Not a player in this game')
    return render_template('game.html', game_id=game_id, player_id=current_player.id_)

@app.route('/img_upload', methods=['POST'])
def image_upload():
    game_id = int(request.form['game_id'])
    player_id = int(request.form['player_id'])

    f = request.files['file']
    image = Image.open(f)
    if image.mode == 'RGBA':
        image = flatten_rgba_image(image)
    # Scale image if necessary
    width_factor = image.size[0] / current_app.config['MAX_IMAGE_WIDTH']
    height_factor = image.size[1] / current_app.config['MAX_IMAGE_HEIGHT']
    max_factor = max(height_factor, width_factor)
    if max_factor > 1:
        target_size = (int(image.size[0] // max_factor), int(image.size[1] // max_factor))
        image = image.resize(target_size)

    bio = io.BytesIO()
    image.save(bio, format='JPEG', quality=Config.JPEG_QUALITY)

    with current_app.db.session_scope() as session:
        game = session.query(Game).get(game_id)
        player = session.query(Player).get(player_id)
        pending_stacks = get_pending_stacks(game, player)

        if pending_stacks:
            stack = pending_stacks[0]
            drawings = Drawing(author=player, stack=stack, drawing=bio.getvalue())
            stack.drawings.append(drawings)
            session.add(drawings)
            session.commit()

    return jsonify({})



@app.context_processor
def inject_external_url():
    return {'server': url_for('index', _external=True).rsplit(':', 1)[0]}

@app.errorhandler(FlashedError)
def handle_flashed_error(exc):
    flash(exc.message, exc.category)
    return redirect(request.url)
