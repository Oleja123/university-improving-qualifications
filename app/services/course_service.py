from flask import current_app
from app import db
from app.dto.course_dto import CourseDTO
from app.models.course import Course
from app.services import course_type_service
import sqlalchemy as sa


def get_all(included=None, course_type=None):
    try:
        query = sa.select(Course).where(sa.and_(sa.or_(included is None, Course.is_included == included), 
                                                sa.or_(course_type is None, Course.course_type_id == course_type))).order_by(Course.course_type_id)
        return db.session.execute(query).scalars().all()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        raise Exception('Неизвестная ошибка')


def get_all_paginated(page: int, included=None, course_types=None):
    try:
        query = sa.select(Course)
        conditions = []
        current_app.logger.info(f"условия {included, course_types}")
        if included is not None:
            conditions.append(Course.is_included == included)

        if course_types is not None:
            conditions.append(Course.course_type_id.in_(course_types))

        current_app.logger.info(f"условия {conditions}")

        if conditions:
            query = query.where(sa.and_(*conditions))
        query = query.order_by(Course.course_type_id)
        return db.paginate(query, page=page, per_page=current_app.config['COURSES_PER_PAGE'], error_out=False)
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        raise Exception('Неизвестная ошибка')


def get_by_id(id: int):
    try:
        res = db.session.get(Course, id)
        if res is None:
            raise ValueError(f'Курс с id = {id} не существует')
        return res
    except ValueError as e:
        db.session.rollback()
        current_app.logger.error(e)
        raise
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        raise Exception('Неизвестная ошибка')
    
def change_included(id: int):
    try:
        res = get_by_id(id)
        res.is_included = not res.is_included
        db.session.commit()
        return res
    except ValueError as e:
        db.session.rollback()
        current_app.logger.error(e)
        raise
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        raise Exception('Неизвестная ошибка')


def get_by_name(name: str):
    try:
        res = db.session.execute(sa.select(Course).where(Course.name == name)).scalar_one_or_none()
        if res is None:
            raise ValueError(f'Курс с именем {name} не существует')
        return res
    except ValueError as e:
        db.session.rollback()
        current_app.logger.error(e)
        raise
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        raise Exception(f'Неизвестная ошибка')


def create(courseDTO: CourseDTO):
    try:
        if courseDTO.course_type_id is None:
            raise ValueError('Не указан id типа курса')
        course_type = course_type_service.get_by_id(courseDTO.course_type_id)
        course = Course(name=courseDTO.name, course_type=course_type)
        db.session.add(course)
        db.session.commit()
    except ValueError as e:
        db.session.rollback()
        current_app.logger.error(e)
        raise
    except sa.exc.IntegrityError as e:
        db.session.rollback()
        current_app.logger.error(e)
        raise ValueError(f'Курс с именем {course.name} уже существует')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        raise Exception(f'Неизвестная ошибка при создании курса')


def update(courseDTO: CourseDTO):
    try:
        record = get_by_id(courseDTO.id)
        if courseDTO.name is not None:
            record.name = courseDTO.name
        if courseDTO.course_type_id is not None:
            course_type = course_type_service.get_by_id(courseDTO.course_type_id)
            record.course_type = course_type
        db.session.commit()
    except ValueError as e:
        db.session.rollback()
        raise
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        raise Exception('Неизвестная ошибка при обновлении курса')


def delete(id: int) -> bool:
    try:
        course = get_by_id(id)
        db.session.delete(course)
        db.session.commit()
    except ValueError as e:
        db.session.rollback()
        raise
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        raise Exception('Неизвестная ошибка при удалении курса')
