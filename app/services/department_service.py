from app import db, app
from app.dto.department_dto import DepartmentDTO
from app.exceptions.role_error import RoleError
from app.models.department import Department
from app.models.user import User
from app.services import faculty_service
from app.dto.user_dto import UserDTO
from app.models import user
import sqlalchemy as sa


def get_all(faculties=None):
    try:
        query = sa.select(Department)
        if faculties is not None:
            query = query.where(Department.faculty_id.in_(faculties))
        return db.session.execute(query).scalars().all()
    except Exception as e:
        db.session.rollback()
        app.logger.error(e)
        raise Exception('Неизвестная ошибка')


def get_all_paginated(page: int, faculties=None):
    try:
        query = sa.select(Department)
        if faculties is not None:
            query = query.where(Department.faculty_id.in_(faculties))
        return db.paginate(query, page=page, per_page=app.config['DEPARTMENTS_PER_PAGE'], error_out=False)
    except Exception as e:
        db.session.rollback()
        app.logger.error(e)
        raise Exception('Неизвестная ошибка')


def get_by_id(id: int):
    try:
        res = db.session.get(Department, id)
        if res is None:
            raise ValueError(f'Кафедра с id = {id} не существует')
        return res
    except ValueError as e:
        db.session.rollback()
        app.logger.error(e)
        raise
    except Exception as e:
        db.session.rollback()
        app.logger.error(e)
        raise Exception('Неизвестная ошибка')


def get_by_name(name: str):
    try:
        res = db.session.execute(sa.select(Department).where(Department.name == name)).scalar_one_or_none()
        if res is None:
            raise ValueError(f'Кафедра с именем {name} не существует')
        return res
    except ValueError as e:
        db.session.rollback()
        app.logger.error(e)
        raise
    except Exception as e:
        db.session.rollback()
        app.logger.error(e)
        raise Exception(f'Неизвестная ошибка')


def create(departmentDTO: DepartmentDTO):
    try:
        if departmentDTO.faculty_id is None:
            raise ValueError('Не указан id факультета')
        faculty = faculty_service.get_by_id(departmentDTO.faculty_id)
        department = Department(name=departmentDTO.name, faculty=faculty)
        db.session.add(department)
        db.session.commit()
    except ValueError as e:
        db.session.rollback()
        app.logger.error(e)
        raise
    except sa.exc.IntegrityError as e:
        db.session.rollback()
        app.logger.error(e)
        raise ValueError(f'Кафедра с именем {departmentDTO.name} уже существует')
    except Exception as e:
        db.session.rollback()
        app.logger.error(e)
        raise Exception(f'Неизвестная ошибка при создании кафедры')

def get_teachers(page: int, department: Department):
    try:
        query = department.teachers.select()
        return db.paginate(query, page=page, per_page=app.config['TEACHERS_PER_PAGE'], error_out=False)
    except Exception as e:
        db.session.rollback()
        app.logger.error(e)
        raise Exception(f'Неизвестная ошибка при получении преподавателей кафедры')


def update(departmentDTO: DepartmentDTO):
    try:
        record = get_by_id(departmentDTO.id)
        if departmentDTO.name is not None:
            record.name = departmentDTO.name
        if departmentDTO.faculty_id is not None:
            faculty = faculty_service.get_by_id(departmentDTO.faculty_id)
            record.faculty = faculty
        db.session.commit()
    except ValueError as e:
        db.session.rollback()
        raise
    except Exception as e:
        db.session.rollback()
        app.logger.error(e)
        raise Exception('Неизвестная ошибка при обновлении кафедры')
    
def add_teacher(id: int, user: User):
    try:
        record = get_by_id(id)
        if(user.role != user.TEACHER):
            raise RoleError('На кафедру добавляется не преподаватель')
        record.teachers.add(user)
        db.session.commit()
    except RoleError as e:
        db.session.rollback()
        app.logger.error(e)
        raise
    except ValueError as e:
        db.session.rollback()
        raise
    except Exception as e:
        db.session.rollback()
        app.logger.error(e)
        raise Exception('Неизвестная ошибка при добавлении преподавателя на кафедру')


def delete(id: int) -> bool:
    try:
        department = get_by_id(id)
        db.session.delete(department)
        db.session.commit()
    except ValueError as e:
        db.session.rollback()
        raise
    except Exception as e:
        db.session.rollback()
        app.logger.error(e)
        raise Exception('Неизвестная ошибка при удалении кафедры')
