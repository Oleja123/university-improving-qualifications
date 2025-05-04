from app import db, app
from app.dto.department_dto import DepartmentDTO
from app.models.department import Department
from app.services import faculty_service
import sqlalchemy as sa


def get_all(faculty=None):
    query = sa.select(Department)
    if faculty is not None:
        query = query.where(Department.faculty_id == faculty)
    return db.session.execute(query).scalars().all()


def get_all_paginated(page: int, faculty=None):
    query = sa.select(Department)
    if faculty is not None:
        query = query.where(Department.faculty_id == faculty)
    return db.paginate(query, page=page, per_page=app.config['DEPARTMENTS_PER_PAGE'], error_out=False)


def get_by_id(id: int):
    return db.session.get(Department, id)


def get_by_name(name: str):
    return db.session.execute(sa.select(Department).where(Department.name == name)).scalar_one_or_none()


def create(departmentDTO: DepartmentDTO):
    if departmentDTO.faculty_id is None:
        return False
    faculty = faculty_service.get_by_id(departmentDTO.faculty_id)
    if faculty is None:
        return False
    department = Department(name=departmentDTO.name, faculty=faculty)
    db.session.add(department)
    db.session.commit()
    return True

def get_teachers(page: int, department: Department):
    query = department.teachers.select()
    return db.paginate(query, page=page, per_page=app.config['TEACHERS_PER_PAGE'], error_out=False)


def update(departmentDTO: DepartmentDTO):
    record = get_by_id(departmentDTO.id)
    if record is None:
        return False
    if departmentDTO.name is not None:
        record.name = departmentDTO.name
    if departmentDTO.faculty_id is not None:
        faculty = faculty_service.get_by_id(departmentDTO.faculty_id)
        record.faculty = faculty
    db.session.commit()
    return True


def delete(id: int) -> bool:
    department = get_by_id(id)
    if (department is None):
        return False
    db.session.delete(department)
    db.session.commit()
    return True
