from datetime import date, datetime
import shutil
import os

from flask import current_app
import sqlalchemy as sa
from werkzeug.utils import secure_filename

from app import db
from app.models import user
from app.models.course_type import CourseType
from app.models.user import User
from app.models.course import Course
from app.services import user_service, course_service
from app.models.teacher_course import TeacherCourse


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


def make_path(user_id: int, course_id: int):
    user_path = os.path.join(
        current_app.config['UPLOAD_FOLDER'], user_id, course_id)
    project_root = os.path.abspath(os.path.join(
        os.path.join(os.path.dirname(__file__), '..'), '..'))
    user_path = os.path.abspath(os.path.join(project_root, user_path))
    return user_path


def upload_file(user_id: int, course_id: int, file):
    try:
        if file.filename == '':
            raise ValueError('Нет выбранного файла')
        if not allowed_file(file.filename):
            raise ValueError('Некорректное расширение файла')

        filename = secure_filename(file.filename)
        user_path = make_path(user_id, course_id)
        if os.path.exists(user_path):
            shutil.rmtree(user_path)
        os.makedirs(user_path, exist_ok=True)
        filepath = os.path.join(user_path, filename)
        file.save(filepath)
        res = get(user_id, course_id)
        res.sertificate_path = filepath
        res.date_completion = None
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
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
        current_app.logger.info(res)
        return res
    except ValueError as e:
        current_app.logger.error(e)
        raise
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        raise Exception('Ошибка при получении курса пользователя')


def get_user_courses(user_id: int, page: int, included=None):
    try:
        query = sa.select(TeacherCourse)
        conditions = []
        conditions.append(TeacherCourse.teacher_id == user_id)
        if included is not None:
            conditions.append(TeacherCourse.course.is_included == included)

        if conditions:
            query = query.where(*conditions)

        return db.paginate(query, page=page, per_page=current_app.config['COURSES_PER_PAGE'], error_out=False)
    except Exception as e:
        current_app.logger.error(e)
        raise Exception('Ошибка при получении курсов пользователя')


def get_all_paginated(page: int, course_name=None, user_full_name=None, course_type_id=None):
    try:

        if course_name is not None and len(course_name) == 0:
            course_name = None

        if user_full_name is not None and len(user_full_name) == 0:
            user_full_name = None

        current_app.logger.info(
            f"page = {page}, course = {course_name}, user = {user_full_name}, course_type = {course_type_id}")

        query = sa.select(TeacherCourse, Course, User).join(Course).join(User)
        conditions = []
        if course_name is not None:
            conditions.append(sa.func.lower(
                Course.name).like(f'%{course_name.lower()}%'))

        if user_full_name is not None:
            conditions.append(sa.func.lower(User.full_name).like(
                f'%{user_full_name.lower()}%'))

        if course_type_id is not None:
            conditions.append(Course.course_type_id == course_type_id)

        current_app.logger.info(f"условия {conditions}")

        if conditions:
            query = query.where(sa.and_(*conditions))

        query = query.order_by(Course.name)
        return db.paginate(query, page=page, per_page=current_app.config['COURSES_PER_PAGE'], error_out=False)
    except Exception as e:
        current_app.logger.error(e)
        raise Exception('Ошибка при получении курсов')


def update_teacher_course(user_id: int, course_id: int, date_completion: datetime):
    try:
        res = get(user_id, course_id)
        if res.sertificate_path is None:
            raise ValueError('Сертификат не прикреплен')
        res.date_completion = date_completion
        db.session.commit()
        return res
    except ValueError as e:
        current_app.logger.error(e)
        raise
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        raise Exception('Неизвестная ошибка')
    

def get_qualification_list():
    cur_date = datetime.now().strftime("%Y-%m-%d")
    try:
        query = sa.text("SELECT public.user.full_name, public.user.username, course.name, course_type.name, teacher_course.date_completion "\
        "FROM public.user CROSS JOIN course JOIN course_type ON course_type.id = course.course_type_id LEFT JOIN teacher_course ON "\
        "teacher_course.teacher_id = public.user.id AND teacher_course.course_id = course.id WHERE public.user.role = :role AND " \
        "(teacher_course.date_completion IS NULL OR EXTRACT(YEAR FROM AGE(:cur_date, teacher_course.date_completion )) >= 3) "\
        "ORDER BY public.user.full_name, public.user.username;")

        qualification_list = db.session.execute(query, {'cur_date': cur_date, 'role': user.TEACHER})
        return qualification_list
    except Exception as e:
        current_app.logger.info(e)
        raise Exception('Ошибка при создании списка прохождения квалификаций')
