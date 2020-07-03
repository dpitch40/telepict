import secrets
import functools

from flask import Blueprint, render_template, request, current_app, flash, \
    session as flask_session, url_for

from ..db import Player
from ..auth import gen_password_hash
from .exceptions import FlashedError
from .util import redirect_page

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    name, password = request.form['name'], request.form['password']
    with current_app.db.session_scope() as session:
        player = session.query(Player).filter_by(name=name).one_or_none()
        # TODO: Log failed login attempts
        if player is None:
            flash('Bad username or password', 'danger')
            return render_template('login.html', redirect_url=request.form['redirect_url'])
        player_hash = player.password_hash
        input_hash = gen_password_hash(password, player.password_salt)
        if not secrets.compare_digest(player_hash, input_hash):
            flash('Bad username or password', 'danger')
            return render_template('login.html', redirect_url=request.form['redirect_url'])
    flask_session['username'] = name
    return redirect_page('Login Successful',
                         'You have logged in successfully. Redirecting in {delay} seconds...',
                         request.form['redirect_url'])

@bp.route('/logout')
def logout():
    flask_session.pop('username', None)
    return redirect_page('Logout Successful',
                         'You have been logged out. Redirecting in {delay} seconds...',
                         url_for('game.index'))

@bp.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if request.method == 'GET':
        return render_template('create_account.html')

    name, dispname, password = request.form['name'], request.form['dispname'], \
        request.form['password']
    with current_app.db.session_scope() as session:
        player = session.query(Player).filter_by(name=name).one_or_none()
        if player is not None:
            raise FlashedError('Username already exists')
        player = Player(name=name, display_name=dispname, password=password)
        session.add(player)
        session.commit()
    flash(f'Account {name} created successfully!', 'primary')
    return render_template('login.html')

def require_logged_in(func):
    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        if 'username' in flask_session:
            return func(*args, **kwargs)

        flash('You must login to view this page', 'warning')
        return render_template('login.html')
    return wrapped
