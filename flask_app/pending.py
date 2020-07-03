from Flask import Blueprint

from .util import inject_current_player
from .auth import require_logged_in

bp = Blueprint('pending', __name__)

@bp.route('/create_game', methods=['get', 'post'])
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

@bp.route('/delete_game/<int:game_id>', methods=['get', 'post'])
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

@bp.route('/pending/<int:game_id>', methods=['get', 'post'])
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

@bp.route('/accept_invite/<int:game_id>', methods=['get', 'post'])
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

@bp.route('/remove_player/<int:game_id>/<int:player_id>', methods=['POST'])
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

@bp.route('/start_game/<int:game_id>', methods=['POST'])
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

@bp.route('/leave_pending_game/<int:game_id>', methods=['POST'])
@inject_current_player
@require_logged_in
def leave_pending_game(session, current_player, game_id):
    game = session.query(PendingGame).get(game_id)
    assn = session.query(PendingGamePlayerAssn).get({'game_id': game.id_,
                                                     'player_id': current_player.id_})
    session.delete(assn)
    session.commit()
    return index()

@bp.route('/invite_player/<int:game_id>', methods=['POST'])
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

@bp.route('/revoke_invitation/<int:game_id>/<int:player_id>', methods=['POST'])
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

@bp.route('/move_player/<int:game_id>/<int:player_id>/<direction>', methods=['POST'])
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
