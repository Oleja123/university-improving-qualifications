from datetime import datetime
from app import app, db
from werkzeug.utils import secure_filename
from app.models import user
from app.models.course import Course
from app.services import user_service, course_service
import sqlalchemy as sa
import shutil
import os

from app.models.teacher_course import TeacherCourse


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def upload_file(user_id: int, course_id: int, file):
    try:
        if file.filename == '':
            raise ValueError('Нет выбранного файла')
        if not allowed_file(file.filename):
            raise ValueError('Некорректное расширение файла')
        app.logger.info('Загрузка файла')
        app.logger.info(file.filename)
        filename = secure_filename(file.filename)
        app.logger.info(filename)
        user_path = os.path.join(app.config['UPLOAD_FOLDER'], user_id, course_id)
        app.logger.info(user_path)
        if os.path.exists(user_path):
            shutil.rmtree(user_path)
        app.logger.info('Создание папки')
        os.makedirs(user_path, exist_ok=True)
        filepath = os.path.join(user_path, filename)
        file.save(filepath)
        res = get(user_id, course_id)
        res.sertificate_path = filepath
        db.session.commit()
    except Exception as e:
        app.logger.info(e)
        raise


def get(user_id: int, course_id: int):
    try:
        res = db.session.get(TeacherCourse, (user_id, course_id))
        if res is None:
            teacher = user_service.get_by_id(user_id)
            if teacher.role != user.TEACHER:
                raise ValueError('Курсы есть только у преподавателя')
            course = course_service.get_by_id(course_id)
            db.session.add(TeacherCourse(teacher=teacher, course=course))
            db.session.commit()
            res = db.session.get(TeacherCourse, (user_id, course_id))
        app.logger.info(res)
        return res
    except ValueError as e:
        raise
    except Exception as e:
        db.session.rollback()
        app.logger.info(e)
        raise Exception('Неизвестная ошибка при получении курса пользователя')


def approve_user_course(user_id: int, course_id: int):
    try:
        res = get(user_id, course_id)
        res.date_approved = datetime.now()
        db.session.commit()
    except ValueError as e:
        raise
    except Exception as e:
        db.session.rollback()
        raise Exception('Неизвестная ошибка при подтверждении курса пользователя')


def get_user_courses(user_id: int, page: int, included=None, approved=None):
    try:
        query = sa.select(TeacherCourse)
        conditions = []
        conditions.append(TeacherCourse.teacher_id == user_id)
        if included is not None:
            conditions.append(TeacherCourse.course.is_included == included)
        if approved is not None:
            if approved:
                conditions.append(TeacherCourse.date_approved.is_not(None))
            else:
                conditions.append(TeacherCourse.date_approved.is_(None))

        if conditions:
            query = query.where(*conditions)
            
        return db.paginate(query, page=page, per_page=app.config['COURSES_PER_PAGE'], error_out=False)
    except Exception as e:
        db.session.rollback()
        app.logger.error(e)
        raise Exception('Неизвестная ошибка')

