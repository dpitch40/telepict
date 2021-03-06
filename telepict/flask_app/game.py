#pylint: disable=no-value-for-parameter

import operator

from flask import Blueprint, request, render_template, session as flask_session, flash, \
    current_app, redirect, url_for, jsonify

from ..db import PendingGame, Invitation, PendingGamePlayerAssn, Player, Game, Stack
from .util import inject_current_player
from .auth import require_logged_in
from .exceptions import FlashedError
from ..util import get_game_state

bp = Blueprint('game', __name__)

@bp.route('/')
def index():
    if 'username' in flask_session:
        view_data = dict()
        with current_app.db.session_scope() as session:
            player = session.query(Player).filter_by(name=flask_session['username']).one_or_none()
            if player:
                invited_games = [i.game for i in player.invitations]

                view_data['games'] = sorted(player.games, key=operator.attrgetter('started'))
                view_data['game_states'] = {g.id_: get_game_state(g, player)['state']
                                            for g in player.games}
                view_data['pending_games'] = sorted(player.pending_games + invited_games,
                                                    key=operator.attrgetter('created'))
                view_data['player'] = player
                view_data['invited_games'] = set(map(operator.attrgetter('id_'), invited_games))
                return render_template('index.html', **view_data)

    return render_template('index.html')

@bp.route('/game/<int:game_id>')
@inject_current_player
@require_logged_in
def view_game(session, current_player, game_id):
    game = session.query(Game).get(game_id)
    if game is None:
        raise FlashedError('Not a player in this game')
    return render_template('game.html', game_id=game_id, player_id=current_player.id_)

@bp.route('/create_game', methods=['get', 'post'])
@inject_current_player
@require_logged_in
def create_game(session, current_player):
    if request.method == 'GET':
        return render_template('create_game.html')

    num_rounds = int(request.form['numrounds'])
    pass_left = request.form['direction'] == 'left'
    write_first = request.form['write_first'] == '1'
    game = PendingGame(num_rounds=num_rounds, pass_left=pass_left, write_first=write_first,
                       creator=current_player, players=[current_player])
    session.add(game)
    session.commit()
    return redirect(url_for('game.pending_game', game_id=game.id_), 303)

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

    session.delete(game)
    session.commit()
    return redirect(url_for('game.index'), 303)

@bp.route('/pending/<int:game_id>', methods=['get', 'post'])
@inject_current_player
@require_logged_in
def pending_game(session, current_player, game_id):
    game = session.query(PendingGame).get(game_id)
    owner = game.creator_id == current_player.id_
    if request.method == 'GET' or not owner:
        if owner:
            past_players = list()
            for past_game in sorted(current_player.games, key=operator.attrgetter('started'),
                                   reverse=True):
                for player in past_game.players:
                    if player != current_player and player not in past_players:
                        past_players.append(player)
            return render_template('edit_pending_game.html', game=game,
                                   past_players=past_players)

        invitation = session.query(Invitation).get({'game_id': game.id_,
                                                    'recipient_id': current_player.id_})
        return render_template('view_pending_game.html', game=game, invitation=invitation)

    game.num_rounds = int(request.form['numrounds'])
    game.pass_left = request.form['direction'] == 'left'
    game.write_first = request.form['write_first'] == '1'
    flash("Updates applied", "primary")
    session.commit()
    return redirect(url_for('game.pending_game', game_id=game_id), 303)

@bp.route('/accept_invite/<int:game_id>', methods=['get', 'post'])
@inject_current_player
@require_logged_in
def respond_invitation(session, current_player, game_id):
    game = session.query(PendingGame).get(game_id)
    invitation = session.query(Invitation).get({'game_id': game.id_,
                                                'recipient_id': current_player.id_})
    reject = request.form.get('action', 'accept') == 'reject'

    if invitation is not None:
        session.delete(invitation)

    if not reject:
        if session.query(PendingGamePlayerAssn).filter_by(player=current_player, game=game). \
                one_or_none() is None:
            session.add(PendingGamePlayerAssn(player_order=len(game.players),
                                              player=current_player, game=game))
    session.commit()
    return redirect(url_for('game.index'), 303)

# AJAX endpoints

@bp.route('/remove_player/<int:game_id>/<int:player_id>', methods=['post'])
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
    return jsonify([p.id_ for p in game.players])

@bp.route('/start_game/<int:game_id>', methods=['post'])
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
    return redirect(url_for('game.view_game', game_id=active_game.id_), 303)

@bp.route('/leave_pending_game/<int:game_id>', methods=['post'])
@inject_current_player
@require_logged_in
def leave_pending_game(session, current_player, game_id):
    game = session.query(PendingGame).get(game_id)
    assn = session.query(PendingGamePlayerAssn).get({'game_id': game.id_,
                                                     'player_id': current_player.id_})
    session.delete(assn)
    session.commit()
    return redirect(url_for('game.index'), 303)

@bp.route('/invite_player/<int:game_id>', methods=['get', 'post'])
@inject_current_player
@require_logged_in
def invite_player(session, current_player, game_id):
    game = session.query(PendingGame).get(game_id)
    if game.creator_id != current_player.id_:
        raise FlashedError('Cannot edit a game you did not create')
    if request.method == 'GET':
        player_name = request.args['name']
    else:
        player_name = request.form['player_name']
    player = session.query(Player).filter_by(name=player_name).one_or_none()
    if player is None:
        flash(f'No player named {player_name!r} exists', 'danger')
    else:
        invitation = Invitation(game=game, recipient=player)
        session.add(invitation)
        session.commit()
    return redirect(url_for('game.pending_game', game_id=game_id), 303)

@bp.route('/revoke_invitation/<int:game_id>/<int:player_id>', methods=['post'])
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
    return redirect(url_for('game.pending_game', game_id=game_id), 303)

@bp.route('/move_player/<int:game_id>/<int:player_id>/<direction>', methods=['post'])
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
    return jsonify({'moved': direction})
