from datetime import datetime
import sqlalchemy as sa

from flask import current_app

from app import db
from app.dto.course_type_dto import CourseTypeDTO
from app.models.course_type import CourseType, add_years


def get_all():
    try:
        return db.session.execute(sa.select(CourseType).order_by(CourseType.name)).scalars().all()
    except Exception as e:
        current_app.logger.error(e)
        raise Exception('Ошибка при получении типов курсов')


def get_by_id(id: int):
    try:
        res = db.session.get(CourseType, id)
        if res is None:
            raise ValueError(f'Тип курсов с id = {id} не существует')
        return res
    except ValueError as e:
        current_app.logger.error(e)
        raise
    except Exception as e:
        current_app.logger.error(e)
        raise Exception('Ошибка при получении типа курсов по id')


def get_by_name(name: str):
    try:
        res = db.session.execute(sa.select(CourseType).where(
            CourseType.name == name)).scalar_one_or_none()
        if res is None:
            raise ValueError(f'Тип курсов с именем {name} не существует')
        return res
    except ValueError as e:
        current_app.logger.error(e)
        raise
    except Exception as e:
        current_app.logger.error(e)
        raise Exception(f'Ошибка при получении курса по названию')


def create(courseTypeDTO: CourseTypeDTO):
    try:
        courseTypeDTO = CourseType(name=courseTypeDTO.name)
        db.session.add(courseTypeDTO)
        db.session.commit()
    except sa.exc.IntegrityError as e:
        db.session.rollback()
        current_app.logger.error(e)
        raise ValueError(
            f'Тип курсов с именем {courseTypeDTO.name} уже существует')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        raise Exception(f'Ошибка при создании тпа курсов')


def update(courseTypeDTO: CourseTypeDTO):
    try:
        record = get_by_id(courseTypeDTO.id)
        record.name = courseTypeDTO.name
        db.session.commit()
    except ValueError as e:
        current_app.logger.error(e)
        raise
    except sa.exc.IntegrityError as e:
        db.session.rollback()
        current_app.logger.error(e)
        raise ValueError(
            f'Тип курсов с именем {courseTypeDTO.name} уже существует')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        raise Exception(f'Ошибка при обновлении типа курсов')


def delete(id: int) -> bool:
    try:
        course_type = get_by_id(id)
        db.session.delete(course_type)
        db.session.commit()
    except ValueError as e:
        current_app.logger.error(e)
        raise
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        raise Exception(f'Ошибка при удалении типа курсов')


def update_deadline(course_typeDTO: CourseTypeDTO):
    try:
        record = None
        if (course_typeDTO.id is not None):
            record = get_by_id(course_typeDTO.id)
        else:
            record = get_by_name(course_typeDTO.name)
        record.deadline = add_years(record.deadline, 3)
        db.session.commit()
    except ValueError as e:
        current_app.logger.error(e)
        raise
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        raise Exception(f'Ошибка при удалении типа курсов')


def set_deadline(course_typeDTO: CourseTypeDTO, deadline: datetime):
    try:
        record = None
        if (course_typeDTO.id is not None):
            record = get_by_id(course_typeDTO.id)
        else:
            record = get_by_name(course_typeDTO.name)
        record.deadline = deadline
        db.session.commit()
    except ValueError as e:
        current_app.logger.error(e)
        raise
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        raise Exception(f'Ошибка при удалении типа курсов')
