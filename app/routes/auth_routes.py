from urllib.parse import urlsplit
from flask import flash, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required, login_user, logout_user
from app.forms import LoginForm
from app.services import user_service
from app import app
from app import login


@login.user_loader
def load_user(id):
  return user_service.get_by_id(id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        try:
            user = user_service.get_by_username(form.username.data)
            user_service.check_password(user.username, form.password.data)
            login_user(user, remember=form.remember_me.data)
            session['user_role'] = user.role
            next_page = request.args.get('next')
            if not next_page or urlsplit(next_page).netloc != '':
                next_page = url_for('index')
            return redirect(url_for('index'))
        except Exception as e:
            flash(e)
            return redirect(url_for('login'))
    return render_template('login.html', title='Вход', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))