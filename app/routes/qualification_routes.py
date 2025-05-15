import os
from flask import flash, jsonify, redirect, render_template, request, send_from_directory, url_for
from flask_login import login_required

from app.decorators.role_decorator import required_role
from app.forms import TeachersCoursesForm, UploadForm
from app.models import user
from app.services import sertificate_service
from app import app


@app.route('/teacher_course/<user_id>/<course_id>', methods=['GET','POST'])
@login_required
@required_role(role=user.TEACHER)
def teacher_course(user_id, course_id):
    teacher_course=sertificate_service.get(user_id, course_id)
    form = UploadForm()
    if teacher_course.date_approved:
        form.file.render_kw = {'disabled': True}
        form.submit.render_kw = {'disabled': True}
    if form.validate_on_submit():
        file = form.file.data
        try:
            if file:
                sertificate_service.upload_file(user_id, course_id, file)
                flash('Файл успешно загружен')
        except ValueError as e:
            app.logger.info(e)
            flash(e)
        except Exception as e:
            app.logger.info(e)
            flash('Ошибка при загрузке файла')
        finally:
            return redirect(url_for('teacher_course', user_id=user_id, course_id=course_id))
    return render_template('teachers_courses/teacher_course.html', title='Курсы преподавателя', teacher_course=teacher_course, form=form)



@app.route('/download_file/<user_id>/<course_id>', methods=['GET','POST'])
@login_required
def download_file(user_id, course_id):
    try:
        user_path = sertificate_service.make_path(user_id, course_id)
        app.logger.info(user_path)
        file = os.listdir(user_path)[0]
        app.logger.info(file)
        return send_from_directory(user_path, file, as_attachment=True)
    except Exception as e:
        app.logger.info(e)
        raise


@app.route('/teachers_courses', methods=['GET','POST'])
@login_required
@required_role(role=user.ADMIN)
def teachers_courses():
    form = TeachersCoursesForm(request.args)
    page = request.args.get('page', 1, type=int)
    course_name = request.args.get('course_name', None, type=str)
    user_full_name = request.args.get('user_full_name', None, type=str)
    course_type_id = request.args.get('course_type_id', None, type=int)
    is_approved = request.args.get('is_approved', None, type=str)


    return render_template('teachers_courses/teachers_courses.html', 
                           title='Курсы преподавателей', form=form, 
                           teachers_courses=sertificate_service.get_all_paginated(page, course_name=course_name, 
                                                                                  user_full_name=user_full_name, 
                                                                                  course_type_id=course_type_id,
                                                                                  is_approved=is_approved))

@app.route('/teachers_courses/approve_course/<user_id>/<course_id>', methods=['POST'])
@login_required
@required_role(role=user.ADMIN)
def approve_course(user_id, course_id):
    try:
        sertificate_service.change_approved(user_id, course_id)
        return jsonify({'success': True })
    except Exception as ex:
        flash(ex)
