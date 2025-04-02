from app import app, db
from flask import flash, redirect, render_template, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from app.forms import LoginForm, EditFacultyForm
import sqlalchemy as sa
from app.models import User, Faculty
from urllib.parse import urlsplit


@app.route('/')
@app.route('/index')
@login_required
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == form.username.data))
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(url_for('index'))
    return render_template('login.html', title='Вход', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/faculties')
@login_required
def faculties():
    faculties = db.session.scalars(sa.select(Faculty).order_by(Faculty.name))
    return render_template('faculties.html', title='Факультеты', faculties=faculties)

@app.route('/faculties/create', methods=['GET', 'POST'])
@login_required
def create_faculty():
    form = EditFacultyForm()
    if form.validate_on_submit():
        faculty = Faculty(name=form.name.data)
        try:
            db.session.add(faculty)
            db.session.commit()
            return redirect(url_for('faculties'))
        except Exception as ex:
            flash(ex)

    return render_template('edit_faculty.html', form=form)


@app.route('/faculties/edit/<faculty_id>', methods=['GET', 'POST'])
@login_required
def edit_faculty(faculty_id):
    form = EditFacultyForm()
    faculty = db.session.get(Faculty, faculty_id)
    if faculty is None:
        return redirect(url_for('faculties'))
    if form.validate_on_submit():
        try:
            faculty.name = form.name.data
            db.session.commit()
            return redirect(url_for('faculties'))
        except Exception as ex:
            flash(ex)
    form.name.data = faculty.name

    return render_template('edit_faculty.html', form=form)

@app.route('/faculties/delete/<faculty_id>', methods=['DELETE', 'GET'])
@login_required
def delete_faculty(faculty_id):
    try:
        faculty = db.session.get(Faculty, faculty_id)
        db.session.delete(faculty)
        db.session.commit()
        return redirect(url_for('faculties'))
    except Exception as ex:
        flash(ex)
