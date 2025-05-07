from app import app
from flask import flash, redirect, render_template, url_for, request
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
            user_service.check_password(user, form.password.data)
            login_user(user, remember=form.remember_me.data)
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


@app.route('/faculties')
@login_required
def faculties():
    return render_template('faculties/faculties.html', title='Факультеты', faculties=faculty_service.get_all())


@app.route('/faculties/create', methods=['GET', 'POST'])
@login_required
def create_faculty():
    form = EditFacultyForm()
    if form.validate_on_submit():
        try:
            faculty_service.create(FacultyDTO.from_form(form))
            return redirect(url_for('faculties'))
        except Exception as ex:
            flash(ex)

    return render_template('faculties/edit_faculty.html', form=form)


@app.route('/faculties/edit/<faculty_id>', methods=['GET', 'POST'])
@login_required
def edit_faculty(faculty_id):
    form = EditFacultyForm()
    if form.validate_on_submit():
        try:
            faculty_service.update(FacultyDTO.from_form(form, faculty_id))
            return redirect(url_for('faculties'))
        except Exception as ex:
            flash(ex)

    form.from_model(faculty_service.get_by_id(faculty_id))
    return render_template('faculties/edit_faculty.html', form=form)


@app.route('/faculties/delete/<faculty_id>', methods=['DELETE', 'GET'])
@login_required
def delete_faculty(faculty_id):
    try:
        faculty_service.delete(faculty_id)
        return redirect(url_for('faculties'))
    except Exception as ex:
        flash(ex)


@app.route('/departments')
@login_required
def departments():
    page = request.args.get('page', 1, type=int)
    faculty = request.args.get('faculty_id', None, type=int)
    if faculty is not None:
        faculty = [faculty]
    departments = department_service.get_all_paginated(page, faculty)
    faculties = faculty_service.get_all()
    return render_template('departments/departments.html', title='Кафедры', departments=departments, faculties=faculties)


@app.route('/departments/create', methods=['GET', 'POST'])
@login_required
def create_department():
    form = EditDepartmentForm()
    if form.validate_on_submit():
        try:
            department_service.create(DepartmentDTO.from_form(form))
            return redirect(url_for('departments'))
        except Exception as ex:
            flash(ex)

    return render_template('departments/edit_department.html', form=form)


@app.route('/departments/edit/<department_id>', methods=['GET', 'POST'])
@login_required
def edit_department(department_id):
    form = EditDepartmentForm()
    if form.validate_on_submit():
        try:
            department = department_service.update(DepartmentDTO.from_form(form, department_id))
            return redirect(url_for('departments'))
        except Exception as ex:
            flash(ex)
    department = department_service.get_by_id(department_id)
    form.from_model(department)

    return render_template('departments/edit_department.html', form=form)


@app.route('/departments/delete/<department_id>', methods=['DELETE', 'GET'])
@login_required
def delete_department(department_id):
    try:
        department_service.delete(department_id)
        return redirect(url_for('departments'))
    except Exception as ex:
        flash(ex)


@app.route('/course_types')
@login_required
def course_types():
    return render_template('types/types.html', title='Типы курсов', types=TypeService.get_all())


@app.route('/course_types/create', methods=['GET', 'POST'])
@login_required
def create_course_type():
    form = EditCourseTypeForm()
    if form.validate_on_submit():
        try:
            TypeService.create(form)
            return redirect(url_for('course_types'))
        except Exception as ex:
            flash(ex)

    return render_template('types/edit_type.html', form=form)


@app.route('/course_types/edit/<type_id>', methods=['GET', 'POST'])
@login_required
def edit_course_type(type_id):
    form = EditCourseTypeForm()
    if form.validate_on_submit():
        try:
            department = TypeService.edit(type_id, form)
            return redirect(url_for('course_types'))
        except Exception as ex:
            flash(ex)
    course_type = TypeService.get_by_id(type_id)
    form.name.data = course_type.name

    return render_template('types/edit_type.html', form=form)


@app.route('/course_types/delete/<type_id>', methods=['DELETE', 'GET'])
@login_required
def delete_course_type(type_id):
    try:
        TypeService.delete(type_id)
        return redirect(url_for('course_types'))
    except Exception as ex:
        flash(ex)