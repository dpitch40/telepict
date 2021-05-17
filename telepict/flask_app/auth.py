import secrets
import functools

from flask import Blueprint, render_template, request, current_app, flash, \
    session as flask_session, url_for, redirect
from pytz import common_timezones, country_timezones

from ..db import Player
from ..auth import gen_password_hash
from .exceptions import FlashedError
from .util import inject_current_player

common_timezones = common_timezones[:]
utc = ['UTC']
american_tzs = country_timezones('us')
european_tzs = [tz for tz in common_timezones if tz.startswith('Europe/')]
australian_tzs = country_timezones('au')
extra_tzs = utc + american_tzs + european_tzs + australian_tzs
for tz in extra_tzs:
    common_timezones.remove(tz)
common_timezones = extra_tzs + common_timezones

bp = Blueprint('auth', __name__)

def require_logged_in(func):
    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        if 'username' in flask_session:
            return func(*args, **kwargs)

        flash('You must login to view this page', 'warning')
        return render_template('login.html')
    return wrapped

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    name, password = request.form['name'], request.form['password']
    with current_app.db.session_scope() as session:
        player = session.query(Player).filter_by(name=name).one_or_none()
        if player is None:
            flash('Bad username or password', 'danger')
            current_app.logger.warning('Failed login attempt: no player named %r', name)
            return render_template('login.html', redirect_url=request.form['redirect_url'])
        player_hash = player.password_hash
        input_hash = gen_password_hash(password, player.password_salt)
        if not secrets.compare_digest(player_hash, input_hash):
            flash('Bad username or password', 'danger')
            current_app.logger.warning('Failed login attempt: invalid password for %r', name)
            return render_template('login.html', redirect_url=request.form['redirect_url'])
        flask_session['username'] = player.name
        flask_session['userdispname'] = player.display_name
    return redirect(request.form['redirect_url'], 303)

@bp.route('/logout')
def logout():
    flask_session.pop('username', None)
    return redirect(url_for('game.index'), 303)

@bp.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if request.method == 'GET':
        return render_template('create_account.html', timezones=common_timezones)

    name, dispname, password, timezone = request.form['name'], request.form['dispname'], \
        request.form['password'], request.form['timezone']
    with current_app.db.session_scope() as session:
        player = session.query(Player).filter_by(name=name).one_or_none()
        if player is not None:
            raise FlashedError('Username already exists')
        player = Player(name=name, display_name=dispname, password=password, timezone=timezone)
        session.add(player)
        session.commit()
        current_app.logger.info('Created player %s (%s)', name, dispname)
    flash(f'Account {name} created successfully!', 'primary')
    return redirect(url_for('auth.login'), 303)

@bp.route('/edit_account', methods=['GET', 'POST'])
@require_logged_in
@inject_current_player
def edit_account(session, player):
    if request.method == 'GET':
        return render_template('edit_account.html', player=player, timezones=common_timezones)

    dispname, new_password, timezone = request.form['dispname'], request.form['password'], \
        request.form['timezone']
    changed = False
    if dispname and dispname != player.display_name:
        player.display_name = dispname
        current_app.logger.info('Player %s changed display name to %s', player.name, dispname)
        changed = True
    if new_password:
        player.password_hash = gen_password_hash(new_password, player.password_salt)
        current_app.logger.info('Player %s changed password', player.name)
        changed = True
    if timezone != player.timezone:
        player.timezone = timezone
        current_app.logger.info('Player %s changed timezone to %s', player.name, timezone)
        changed = True
    if changed:
        session.commit()
        flask_session['userdispname'] = player.display_name
        flash('Account changes applied', 'primary')
    return redirect(url_for('auth.edit_account'), 303)
