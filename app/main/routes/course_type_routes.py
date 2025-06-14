from flask import flash, jsonify, redirect, render_template, url_for
from flask_login import login_required

from app.decorators.role_decorator import required_role
from app.dto.course_type_dto import CourseTypeDTO
from app.main.forms import EditCourseTypeForm
from app.models import user
from app.services import course_type_service
from app.main import bp


@bp.route('/course_types')
@login_required
@required_role(role=user.ADMIN)
def course_types():
    return render_template('course_types/course_types.html', 
                           title='Типы курсов', 
                           course_types=course_type_service.get_all())


@bp.route('/course_types/create', methods=['GET', 'POST'])
@login_required
@required_role(role=user.ADMIN)
def create_course_type():
    form = EditCourseTypeForm()
    if form.validate_on_submit():
        try:
            course_type_service.create(CourseTypeDTO.from_form(form))
            return redirect(url_for('main.course_types'))
        except Exception as e:
            flash(str(e))
            return redirect(url_for('main.create_course_type'))

    return render_template('course_types/edit_course_type.html', 
                           title='Создать тип курсов', 
                           form=form)


@bp.route('/course_types/edit/<course_type_id>', methods=['GET', 'POST'])
@login_required
@required_role(role=user.ADMIN)
def edit_course_type(course_type_id):
    form = EditCourseTypeForm()
    if form.validate_on_submit():
        try:
            course_type = course_type_service.update(
                CourseTypeDTO.from_form(form, course_type_id))
            return redirect(url_for('main.course_types'))
        except Exception as e:
            flash(str(e))
            return redirect(url_for('main.edit_course_type', course_type_id=course_type_id))
    try:
        course_type = course_type_service.get_by_id(course_type_id)
        form.from_model(course_type)
    except ValueError as e:
        flash(e)
        return redirect(url_for('main.course_types'))
    except Exception as e:
        flash('Ошибка при редактировании типа курса')
        return redirect(url_for('main.course_types'))

    return render_template('course_types/edit_course_type.html', 
                           title='Редактировать тип курсов', 
                           form=form)


@bp.route('/course_types/delete/<course_type_id>', methods=['DELETE'])
@login_required
@required_role(role=user.ADMIN)
def delete_course_type(course_type_id):
    try:
        course_type_service.delete(course_type_id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
