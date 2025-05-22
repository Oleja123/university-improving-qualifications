from flask import flash, jsonify, redirect, render_template, request, url_for
from flask_login import login_required

from app.decorators.role_decorator import required_role
from app.dto.department_dto import DepartmentDTO
from app.main.forms import EditDepartmentForm
from app.models import user
from app.services import department_service, faculty_service
from app.main import bp


@bp.route('/departments')
@login_required
@required_role(role=user.ADMIN)
def departments():
    page = request.args.get('page', 1, type=int)
    faculty = request.args.get('faculty_id', None, type=int)
    if faculty is not None:
        faculty = [faculty]
    departments = department_service.get_all_paginated(page, faculty)
    faculties = faculty_service.get_all()
    return render_template('departments/departments.html', title='Кафедры', departments=departments, faculties=faculties)


@bp.route('/departments/create', methods=['GET', 'POST'])
@login_required
@required_role(role=user.ADMIN)
def create_department():
    form = EditDepartmentForm()
    if form.validate_on_submit():
        try:
            department_service.create(DepartmentDTO.from_form(form))
            return redirect(url_for('main.departments'))
        except Exception as e:
            flash(str(e))
            return redirect(url_for('main.create_department'))

    return render_template('departments/edit_department.html', form=form)


@bp.route('/departments/edit/<department_id>', methods=['GET', 'POST'])
@login_required
@required_role(role=user.ADMIN)
def edit_department(department_id):
    form = EditDepartmentForm()
    if form.validate_on_submit():
        try:
            department = department_service.update(
                DepartmentDTO.from_form(form, department_id))
            return redirect(url_for('main.departments'))
        except Exception as e:
            flash(str(e))
            return redirect(url_for('main.edit_department', department_id=department_id))

    department = department_service.get_by_id(department_id)
    form.from_model(department)

    return render_template('departments/edit_department.html', form=form)


@bp.route('/departments/delete/<department_id>', methods=['DELETE'])
@login_required
@required_role(role=user.ADMIN)
def delete_department(department_id):
    try:
        department_service.delete(department_id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
