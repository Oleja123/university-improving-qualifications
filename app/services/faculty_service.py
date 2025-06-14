from flask import current_app
import sqlalchemy as sa

from app import db
from app.models.faculty import Faculty
from app.dto.faculty_dto import FacultyDTO


def get_all():
    try:
        return db.session.execute(sa.select(Faculty).order_by(Faculty.name)).scalars().all()
    except Exception as e:
        current_app.logger.error(e)
        raise Exception('Ошибка при получении факультетов')


def get_by_id(id: int):
    try:
        res = db.session.get(Faculty, id)
        if res is None:
            raise ValueError(f'Факультет с id = {id} не существует')
        return res
    except ValueError as e:
        current_app.logger.error(e)
        raise
    except Exception as e:
        current_app.logger.error(e)
        raise Exception('Ошибка при получении факультета по id')


def get_by_name(name: str):
    try:
        res = db.session.execute(sa.select(Faculty).where(
            Faculty.name == name)).scalar_one_or_none()
        if res is None:
            raise ValueError(f'Факультет с именем {name} не существует')
        return res
    except ValueError as e:
        current_app.logger.error(e)
        raise
    except Exception as e:
        current_app.logger.error(e)
        raise Exception(f'Ошибка при получении факультета по названию')


def create(facultyDTO: FacultyDTO):
    try:
        faculty = Faculty(name=facultyDTO.name)
        db.session.add(faculty)
        db.session.commit()
    except sa.exc.IntegrityError as e:
        db.session.rollback()
        current_app.logger.error(e)
        raise ValueError(
            f'Факультет с именем {facultyDTO.name} уже существует')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        raise Exception(f'Ошибка при создании факультета')


def update(facultyDTO: FacultyDTO):
    try:
        record = get_by_id(facultyDTO.id)
        record.name = facultyDTO.name
        db.session.commit()
    except ValueError as e:
        current_app.logger.error(e)
        raise
    except sa.exc.IntegrityError as e:
        db.session.rollback()
        current_app.logger.error(e)
        raise ValueError(
            f'Факультет с именем {facultyDTO.name} уже существует')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        raise Exception(f'Ошибка при обновлении факультета')


def delete(id: int) -> bool:
    try:
        faculty = get_by_id(id)
        db.session.delete(faculty)
        db.session.commit()
    except ValueError as e:
        current_app.logger.error(e)
        raise
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        raise Exception(f'Ошибка при удалении факультета')


def get_departments(facultyDTO: FacultyDTO):
    try:
        faculty = None
        if facultyDTO.id is not None:
            faculty = get_by_id(facultyDTO.id)
        else:
            faculty = get_by_name(facultyDTO.name)
        return db.session.scalars(faculty.departments.select()).all()
    except ValueError as e:
        current_app.logger.error(e)
        raise
    except Exception as e:
        current_app.logger.error(e)
        raise Exception(f'Ошибка при получении кафедр факультета')
