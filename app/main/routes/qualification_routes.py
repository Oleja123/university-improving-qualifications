import os
from flask import abort, current_app, flash, jsonify, redirect, render_template, request, send_from_directory, url_for
from flask_login import current_user, login_required

from app.decorators.role_decorator import required_role
from app.decorators.user_decorator import user_required
from app.main.forms import TeacherCourseForm, TeachersCoursesForm, UploadForm
from app.models import user
from app.services import sertificate_service
from app.main import bp


@bp.route('/teacher_course/<user_id>/<course_id>', methods=['GET', 'POST'])
@login_required
@required_role(role=user.TEACHER)
@user_required
def teacher_course(user_id, course_id):        
    teacher_course = sertificate_service.get(user_id, course_id)
    form = UploadForm()
    if form.validate_on_submit():
        file = form.file.data
        try:
            if file:
                sertificate_service.upload_file(user_id, course_id, file)
                flash('Файл успешно загружен')
        except ValueError as e:
            flash(str(e))
        except Exception as e:
            flash('Ошибка при загрузке файла')
        finally:
            return redirect(url_for('main.teacher_course', user_id=user_id, course_id=course_id))
    return render_template('teachers_courses/teacher_course.html', 
                           title='Курсы преподавателя', 
                           teacher_course=teacher_course, form=form)


@bp.route('/teacher_course/<user_id>/<course_id>/completion', methods=['GET', 'POST'])
@login_required
@required_role(role=user.ADMIN)
def teacher_course_completion(user_id, course_id):
    try:
        teacher_course = sertificate_service.get(user_id, course_id)
    except ValueError as e:
        abort(403)
    except Exception as e:
        abort(500)

    form = TeacherCourseForm()
    if not teacher_course.sertificate_path:
        abort(403)

    if form.validate_on_submit():
        date = form.date_completion
        try:
            sertificate_service.update_teacher_course(user_id, course_id, date.data)
            flash('Дата прохождения успешно обновлена')
            return redirect(url_for('main.teachers_courses'))
        except ValueError as e:
            flash(str(e))
            return redirect(url_for('main.teacher_course_completion', user_id=user_id, course_id=course_id))
        except Exception as e:
            flash('Ошибка при обновлении курса преподавателя')
            return redirect(url_for('main.teacher_course_completion', user_id=user_id, course_id=course_id))
    return render_template('teachers_courses/teacher_course_approve.html', 
                           title='Курс преподавателя', 
                           teacher_course=teacher_course, form=form)


@bp.route('/download_file/<user_id>/<course_id>', methods=['GET', 'POST'])
@login_required
def download_file(user_id, course_id):
    try:
        if current_user.role != user.ADMIN and str(current_user.id) != str(user_id):
            abort(403)
        user_path = sertificate_service.make_path(user_id, course_id)
        current_app.logger.info(user_path)
        file = os.listdir(user_path)[0]
        current_app.logger.info(file)
        return send_from_directory(user_path, file, as_attachment=True)
    except Exception as e:
        current_app.logger.info(e)
        return jsonify({"error": str(e)}), 500


@bp.route('/teachers_courses', methods=['GET', 'POST'])
@login_required
@required_role(role=user.ADMIN)
def teachers_courses():
    form = TeachersCoursesForm(request.args)
    page = request.args.get('page', 1, type=int)
    course_name = request.args.get('course_name', None, type=str)
    user_full_name = request.args.get('user_full_name', None, type=str)
    course_type_id = request.args.get('course_type_id', None, type=int)

    return render_template('teachers_courses/teachers_courses.html',
                           title='Курсы преподавателей', 
                           form=form,
                           teachers_courses=sertificate_service.get_all_paginated(page, course_name=course_name,
                                                                                  user_full_name=user_full_name,
                                                                                  course_type_id=course_type_id))