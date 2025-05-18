from urllib.parse import urlsplit
from flask import current_app, flash, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app.auth.forms import LoginForm
from app.exceptions.wrong_password_error import WrongPasswordError
from app.services import user_service
from app import login
from app.auth import bp


@login.user_loader
def load_user(id):
    return user_service.get_by_id(id)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        try:
            user = user_service.get_by_username(form.username.data)
            user_service.check_password(user.username, form.password.data)
            login_user(user, remember=form.remember_me.data)
            session['user_role'] = user.role
            session['user_id'] = user.id
            r = current_app.config['SESSION_REDIS']
            r.sadd(f"user_session:{user.id}", session.sid)
            next_page = request.args.get('next')
            if not next_page or urlsplit(next_page).netloc != '':
                next_page = url_for('main.index')
            return redirect(next_page)
        except Exception as e:
            flash(str(e))
            return redirect(url_for('auth.login'))
    return render_template('auth/login.html', title='Вход', form=form)


@bp.route('/logout')
@login_required
def logout():
    r = current_app.config['SESSION_REDIS']
    session_id = session.sid
    current_user_id = current_user.id
    
    logout_user()

    session.clear()

    r.delete(f"session:{session_id}")
    r.srem(f"user_session:{current_user_id}", session_id)

    return redirect(url_for('main.index'))
