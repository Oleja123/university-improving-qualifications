import os
from flask import flash, redirect, render_template, request, send_from_directory, url_for
from flask_login import login_required

from app.decorators.role_decorator import required_role
from app.forms import UploadForm
from app.models import user
from app.services import course_service, sertificate_service
from app import app


@app.route('/teacher_course/<user_id>/<course_id>', methods=['GET','POST'])
@login_required
@required_role(role=user.TEACHER)
def teacher_course(user_id, course_id):
    teacher_course=sertificate_service.get(user_id, course_id)
    form = UploadForm()
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
@required_role(role=user.TEACHER)
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

