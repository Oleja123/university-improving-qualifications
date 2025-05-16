from flask import flash, jsonify, redirect, render_template, request, url_for
from flask_login import login_required

from app.decorators.role_decorator import required_role
from app.dto.course_dto import CourseDTO
from app.main.forms import EditCourseForm
from app.models import user
from app.services import course_service, course_type_service
from app.main import bp


@bp.route('/courses')
@login_required
def courses():
    page = request.args.get('page', 1, type=int)
    course_type = request.args.get('course_type_id', None, type=int)
    is_included = request.args.get('is_included', None, type=str)
    if is_included == '':
        is_included = None
    if is_included is not None and is_included == 'True':
        is_included = True
    if is_included is not None and is_included == 'False':
        is_included = False
    if course_type is not None:
        course_type = [course_type]
    courses = course_service.get_all_paginated(page, is_included, course_type)
    course_types = course_type_service.get_all()
    return render_template('courses/courses.html', title='Курсы', courses=courses, course_types=course_types)


@bp.route('/courses/create', methods=['GET', 'POST'])
@login_required
@required_role(role=user.ADMIN)
def create_course():
    form = EditCourseForm()
    if form.validate_on_submit():
        try:
            course_service.create(CourseDTO.from_form(form))
            return redirect(url_for('main.courses'))
        except Exception as e:
            flash(str(e))
            return redirect(url_for('main.create_course'))

    return render_template('courses/edit_course.html', form=form)


@bp.route('/courses/edit/<course_id>', methods=['GET', 'POST'])
@login_required
@required_role(role=user.ADMIN)
def edit_course(course_id):
    form = EditCourseForm()
    if form.validate_on_submit():
        try:
            course_service.update(CourseDTO.from_form(form, course_id))
            return redirect(url_for('main.courses'))
        except Exception as e:
            flash(str(e))
            return redirect(url_for('main.edit_course', course_id=course_id))
    course = course_service.get_by_id(course_id)
    form.from_model(course)

    return render_template('courses/edit_course.html', form=form)


@bp.route('/courses/delete/<course_id>', methods=['DELETE'])
@login_required
@required_role(role=user.ADMIN)
def delete_course(course_id):
    try:
        course_service.delete(course_id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route('/courses/include/<course_id>', methods=['POST'])
@login_required
@required_role(role=user.ADMIN)
def include_course(course_id):
    try:
        course_service.change_included(course_id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
