from app import app
from flask import flash, redirect, render_template, session, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from app.dto.department_dto import DepartmentDTO
from app.dto.faculty_dto import FacultyDTO
from app.forms import LoginForm, EditFacultyForm, EditDepartmentForm, EditCourseTypeForm
import sqlalchemy as sa
from app.models import User, Faculty, Department
from app.services import faculty_service, user_service, department_service
from urllib.parse import urlsplit
from app import login


@app.route('/')
@app.route('/index')
@login_required
def index():
    return render_template('index.html')


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

import app.routes.faculty_routes, app.routes.department_routes, app.routes.course_type_routes, app.routes.course_routes, app.routes.user_routes, app.routes.qualification_routes
import app.routes.notification_routes
