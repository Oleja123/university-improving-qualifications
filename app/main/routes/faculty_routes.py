from flask import flash, jsonify, redirect, render_template, request, url_for
from flask_login import login_required

from app.decorators.role_decorator import required_role
from app.dto.faculty_dto import FacultyDTO
from app.main.forms import EditFacultyForm
from app.models import user
from app.services import faculty_service
from app.main import bp


@bp.route('/faculties')
@login_required
@required_role(role=user.ADMIN)
def faculties():
    return render_template('faculties/faculties.html', 
                           title='Факультеты', 
                           faculties=faculty_service.get_all())


@bp.route('/faculties/create', methods=['GET', 'POST'])
@login_required
@required_role(role=user.ADMIN)
def create_faculty():
    form = EditFacultyForm()
    if form.validate_on_submit():
        try:
            faculty_service.create(FacultyDTO.from_form(form))
            return redirect(url_for('main.faculties'))
        except Exception as e:
            flash(str(e))
            return redirect(url_for('main.create_faculty'))

    return render_template('faculties/edit_faculty.html', 
                           title='Создать факультет', 
                           form=form)


@bp.route('/faculties/edit/<faculty_id>', methods=['GET', 'POST'])
@login_required
@required_role(role=user.ADMIN)
def edit_faculty(faculty_id):
    form = EditFacultyForm()
    if form.validate_on_submit():
        try:
            faculty_service.update(FacultyDTO.from_form(form, faculty_id))
            return redirect(url_for('main.faculties'))
        except Exception as e:
            flash(str(e))
            return redirect(url_for('main.edit_faculty', faculty_id=faculty_id))
    try:
        form.from_model(faculty_service.get_by_id(faculty_id))
    except ValueError as e:
        flash(e)
        return redirect(request.referrer or url_for('main.faculties'))
    except Exception as e:
        flash('Ошибка при редактировании факультета')
        return redirect(request.referrer or url_for('main.faculties'))
    
    return render_template('faculties/edit_faculty.html', 
                           title='Редактировать факультет', 
                           form=form)


@bp.route('/faculties/delete/<faculty_id>', methods=['DELETE'])
@login_required
@required_role(role=user.ADMIN)
def delete_faculty(faculty_id):
    try:
        faculty_service.delete(faculty_id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
