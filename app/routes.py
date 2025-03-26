from app import app
from flask import flash, redirect, render_template, url_for
from app.forms import LoginForm


@app.route('/')
@app.route('/index')
def index():
    user = {'username': 'Oleja'}
    courses = [
        {'name': 'Пожарная безопасность 2025',
         'type': 'Безопасность'},
        {'name': 'Дискретная математика 2025',
         'type': 'Учебные'},
        {'name': 'Функциональное прогаммирование 2025',
         'type': 'Учебные'},
    ]
    return render_template('index.html', user=user, courses=courses)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Вход для пользователя {}, запомнить меня = {}'.format(
        form.username.data, form.remember_me.data))
        return redirect(url_for('index '))
    return render_template('login.html', form=form)
