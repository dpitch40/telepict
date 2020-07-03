import functools
import io

from flask import Flask, render_template, request, flash, redirect, session as flask_session, \
    current_app, url_for, jsonify
from PIL import Image

from config import Config
from .auth import bp as auth_bp, require_logged_in
from db import DB, Player, Game, PendingGame, PendingGamePlayerAssn, Invitation, Stack, Drawing
from .exceptions import FlashedError
from util import get_pending_stacks
from util.image import flatten_rgba_image

app = Flask('Telepict')
app.config.from_object(Config)
app.db = DB()

app.register_blueprint(auth_bp)

def inject_current_player(func):
    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        with current_app.db.session_scope() as session:
            if 'username' in flask_session:
                current_player = session.query(Player).filter_by(name=flask_session['username']).one_or_none()
            else:
                current_player = None
            return func(session, current_player, *args, **kwargs)
    return wrapped

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

@app.route('/create_game', methods=['get', 'post'])
@inject_current_player
@require_logged_in
def create_game(session, current_player):
    if request.method == 'GET':
        return render_template('create_game.html')
    else:
        num_rounds = int(request.form['numrounds'])
        pass_left = request.form['direction'] == 'left'
        write_first = request.form['write_first'] == '1'
        game = PendingGame(num_rounds=num_rounds, pass_left=pass_left, write_first=write_first,
                           creator=current_player, players=[current_player])
        session.add(game)
        session.commit()
        return pending_game(game.id_)

@app.route('/delete_game/<int:game_id>', methods=['get', 'post'])
@inject_current_player
@require_logged_in
def delete_game(session, current_player, game_id):
    game = session.query(PendingGame).get(game_id)
    owner = game.creator_id == current_player.id_
    if not owner:
        raise FlashedError('Cannot delete a game you did not create')
    if request.method == 'GET':
        return render_template('delete_game.html', game=game)
    else:
        session.delete(game)
        session.commit()
        return index()

@app.route('/pending/<int:game_id>', methods=['get', 'post'])
@inject_current_player
@require_logged_in
def pending_game(session, current_player, game_id):
    game = session.query(PendingGame).get(game_id)
    owner = game.creator_id == current_player.id_
    if request.method == 'GET' or not owner:
        if owner:
            return render_template('edit_pending_game.html', game=game)
        else:
            invitation = session.query(Invitation).get({'game_id': game.id_,
                                                        'recipient_id': current_player.id_})
            return render_template('view_pending_game.html', game=game, invitation=invitation)
    else:
        game.num_rounds = int(request.form['numrounds'])
        game.pass_left = request.form['direction'] == 'left'
        game.write_first = request.form['write_first'] == '1'
        flash("Updates applied", "info")
        session.commit()
        return render_template('edit_pending_game.html', game=game)

@app.route('/accept_invite/<int:game_id>', methods=['get', 'post'])
@inject_current_player
@require_logged_in
def accept_invitation(session, current_player, game_id):
    game = session.query(PendingGame).get(game_id)
    invitation = session.query(Invitation).get({'game_id': game.id_,
                                                'recipient_id': current_player.id_})
    if invitation is not None:
        session.delete(invitation)
    if not request.args.get('reject', False):
        session.add(PendingGamePlayerAssn(player_order=len(game.players),
                                          player=current_player, game=game))
    session.commit()
    return index()

@app.route('/remove_player/<int:game_id>/<int:player_id>', methods=['POST'])
@inject_current_player
@require_logged_in
def remove_player(session, current_player, game_id, player_id):
    game = session.query(PendingGame).get(game_id)
    if game.creator_id != current_player.id_:
        raise FlashedError('Cannot edit a game you did not create')
    player = session.query(Player).get(player_id)
    assn = session.query(PendingGamePlayerAssn).get({'game_id': game.id_,
                                                     'player_id': player.id_})
    session.delete(assn)
    session.commit()
    return render_template('edit_pending_game.html', game=game)

@app.route('/start_game/<int:game_id>', methods=['POST'])
@inject_current_player
@require_logged_in
def start_game(session, current_player, game_id):
    game = session.query(PendingGame).get(game_id)
    if game.creator_id != current_player.id_:
        raise FlashedError('Cannot edit a game you did not create')
    active_game = Game(num_rounds=game.num_rounds, pass_left=game.pass_left,
                       write_first=game.write_first, players=game.players)
    session.add(active_game)
    session.delete(game)
    for player in active_game.players:
        stack = Stack(game=active_game, owner=player)
        session.add(stack)
    session.commit()
    return view_game(active_game.id_)

@app.route('/leave_pending_game/<int:game_id>', methods=['POST'])
@inject_current_player
@require_logged_in
def leave_pending_game(session, current_player, game_id):
    game = session.query(PendingGame).get(game_id)
    assn = session.query(PendingGamePlayerAssn).get({'game_id': game.id_,
                                                     'player_id': current_player.id_})
    session.delete(assn)
    session.commit()
    return index()

@app.route('/invite_player/<int:game_id>', methods=['POST'])
@inject_current_player
@require_logged_in
def invite_player(session, current_player, game_id):
    game = session.query(PendingGame).get(game_id)
    if game.creator_id != current_player.id_:
        raise FlashedError('Cannot edit a game you did not create')
    player_name = request.form['player_name']
    player = session.query(Player).filter_by(name=player_name).one_or_none()
    if player is None:
        flash(f'No player named {player_name!r} exists', 'error')
    else:
        invitation = Invitation(game=game, recipient=player)
        session.add(invitation)
        session.commit()
    return render_template('edit_pending_game.html', game=game)

@app.route('/revoke_invitation/<int:game_id>/<int:player_id>', methods=['POST'])
@inject_current_player
@require_logged_in
def revoke_invitation(session, current_player, game_id, player_id):
    game = session.query(PendingGame).get(game_id)
    if game.creator_id != current_player.id_:
        raise FlashedError('Cannot edit a game you did not create')
    player = session.query(Player).get(player_id)
    invitation = session.query(Invitation).get({'game_id': game.id_,
                                                'recipient_id': player.id_})
    session.delete(invitation)
    session.commit()
    return render_template('edit_pending_game.html', game=game)

@app.route('/move_player/<int:game_id>/<int:player_id>/<direction>', methods=['POST'])
@inject_current_player
@require_logged_in
def move_player(session, current_player, game_id, player_id, direction):
    game = session.query(PendingGame).get(game_id)
    player = session.query(Player).filter_by(name=flask_session['username']).one()
    if game.creator_id != current_player.id_:
        raise FlashedError('Cannot edit a game you did not create')
    player = session.query(Player).get(player_id)
    assn = session.query(PendingGamePlayerAssn).get({'game_id': game.id_,
                                                     'player_id': player.id_})
    if direction == 'up':
        po = assn.player_order - 1
    else:
        po = assn.player_order + 1
    other_assn = session.query(PendingGamePlayerAssn).filter_by(game_id=game.id_,
                                                                player_order=po).one()
    assn.player_order, other_assn.player_order = other_assn.player_order, assn.player_order
    session.commit()
    return render_template('edit_pending_game.html', game=game)

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
        print(target_size)
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
