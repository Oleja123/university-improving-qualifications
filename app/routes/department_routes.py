from flask import flash, jsonify, redirect, render_template, request, url_for
from app import app
from flask_login import login_required

from app.dto.department_dto import DepartmentDTO
from app.forms import EditDepartmentForm
from app.services import department_service, faculty_service


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


@app.route('/departments/delete/<department_id>', methods=['DELETE'])
@login_required
def delete_department(department_id):
    try:
        department_service.delete(department_id)
        return jsonify({'success': True })
    except Exception as ex:
        flash(ex)