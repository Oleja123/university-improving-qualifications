from datetime import datetime
from flask import current_app
import sqlalchemy as sa

from app import db
from app.dto.course_dto import CourseDTO
from app.models.course import Course
from app.models.course_type import CourseType
from app.models.teacher_course import TeacherCourse
from app.services import course_type_service


def get_all_paginated(page: int, course_types=None):
    try:
        if course_types is not None and not isinstance(course_types, list):
            course_types = [course_types]
        query = sa.select(Course)
        conditions = []
        current_app.logger.info(f"условия { course_types }")

        if course_types is not None:
            conditions.append(Course.course_type_id.in_(course_types))


        current_app.logger.info(f"условия {conditions}")

        if conditions:
            query = query.where(sa.and_(*conditions))
        query = query.order_by(Course.name)
        return db.paginate(query, page=page, per_page=current_app.config['COURSES_PER_PAGE'], error_out=False)
    except Exception as e:
        current_app.logger.error(e)
        raise Exception('Ошибка при получении курсов')


def get_by_id(id: int):
    try:
        res = db.session.get(Course, id)
        if res is None:
            raise ValueError(f'Курс с id = {id} не существует')
        return res
    except ValueError as e:
        current_app.logger.error(e)
        raise
    except Exception as e:
        current_app.logger.error(e)
        raise Exception('Ошибка при получении курса по id')


def get_by_name(name: str):
    try:
        res = db.session.execute(sa.select(Course).where(
            Course.name == name)).scalar_one_or_none()
        if res is None:
            raise ValueError(f'Курс с именем {name} не существует')
        return res
    except ValueError as e:
        current_app.logger.error(e)
        raise
    except Exception as e:
        current_app.logger.error(e)
        raise Exception(f'Ошибка при получении курса по названию')


def create(courseDTO: CourseDTO):
    try:
        if courseDTO.course_type_id is None:
            raise ValueError('Не указан id типа курса')
        course_type = course_type_service.get_by_id(courseDTO.course_type_id)
        course = Course(name=courseDTO.name, course_type=course_type)
        db.session.add(course)
        db.session.commit()
    except ValueError as e:
        current_app.logger.error(e)
        raise
    except sa.exc.IntegrityError as e:
        db.session.rollback()
        current_app.logger.error(e)
        raise ValueError(f'Курс с именем {course.name} уже существует')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        raise Exception(f'Ошибка при создании курса')


def update(courseDTO: CourseDTO):
    try:
        record = get_by_id(courseDTO.id)
        if courseDTO.name is not None:
            record.name = courseDTO.name
        if courseDTO.course_type_id is not None:
            course_type = course_type_service.get_by_id(
                courseDTO.course_type_id)
            record.course_type = course_type
        db.session.commit()
    except ValueError as e:
        current_app.logger.error(e)
        raise
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        raise Exception('Ошибка при обновлении курса')


def delete(id: int) -> bool:
    try:
        course = get_by_id(id)
        db.session.delete(course)
        db.session.commit()
    except ValueError as e:
        current_app.logger.error(e)
        raise
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        raise Exception('Ошибка при удалении курса')
