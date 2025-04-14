from app import app, db
from flask import flash, redirect, render_template, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from app.forms import LoginForm, EditFacultyForm, EditDepartmentForm, EditCourseTypeForm
import sqlalchemy as sa
from app.models import User, Faculty, Department
from app.services import DepartmentService, FacultyService, TypeService
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
    return render_template('faculties/faculties.html', title='Факультеты', faculties=FacultyService.get_all())


@app.route('/faculties/create', methods=['GET', 'POST'])
@login_required
def create_faculty():
    form = EditFacultyForm()
    if form.validate_on_submit():
        try:
            FacultyService.create(form)
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
            faculty = FacultyService.edit(faculty_id, form)
            if faculty is None:
                return redirect(url_for('faculties'))
            return redirect(url_for('faculties'))
        except Exception as ex:
            flash(ex)
    form.name.data = FacultyService.get_by_id(faculty_id).name

    return render_template('faculties/edit_faculty.html', form=form)


@app.route('/faculties/delete/<faculty_id>', methods=['DELETE', 'GET'])
@login_required
def delete_faculty(faculty_id):
    try:
        FacultyService.delete(faculty_id)
        return redirect(url_for('faculties'))
    except Exception as ex:
        flash(ex)


@app.route('/departments')
@login_required
def departments():
    return render_template('departments/departments.html', title='Кафедры', departments=DepartmentService.get_all())


@app.route('/departments/create', methods=['GET', 'POST'])
@login_required
def create_department():
    form = EditDepartmentForm()
    if form.validate_on_submit():
        try:
            DepartmentService.create(form)
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
            department = DepartmentService.edit(department_id, form)
            return redirect(url_for('departments'))
        except Exception as ex:
            flash(ex)
    department = DepartmentService.get_by_id(department_id)
    form.name.data = department.name
    form.faculty.data = department.faculty_id

    return render_template('departments/edit_department.html', form=form)


@app.route('/departments/delete/<department_id>', methods=['DELETE', 'GET'])
@login_required
def delete_department(department_id):
    try:
        DepartmentService.delete(department_id)
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