from flask import Flask, render_template, request, flash, redirect, session as flask_session, \
    current_app

from config import Config
from .auth import bp as auth_bp, require_logged_in
from db import DB, Player, Game, PendingGame
from .exceptions import FlashedError

app = Flask('Telepict')
app.config.from_object(Config)
app.db = DB()

app.register_blueprint(auth_bp)

@app.route('/')
def index():
    if 'username' in flask_session:
        view_data = dict()
        with current_app.db.session_scope() as session:
            player = session.query(Player).filter_by(name=flask_session['username']).one()
            view_data['games'] = player.games
            view_data['pending_games'] = player.pending_games
            return render_template('index.html', **view_data)
    else:
        return render_template('index.html')

@app.route('/game/<game_id>')
@require_logged_in
def view_game(game_id):
    with current_app.db.session_scope() as session:
        game = session.query(Game).get(game_id)
        return str(game)

@app.route('/pending/<game_id>')
@require_logged_in
def view_pending_game(game_id):
    with current_app.db.session_scope() as session:
        game = session.query(PendingGame).get(game_id)
        return str(game)

@app.errorhandler(FlashedError)
def handle_flashed_error(exc):
    flash(exc.message, exc.category)
    return redirect(request.url)
