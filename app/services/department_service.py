from app import db
from app.dto.department_dto import DepartmentDTO
from app.models.department import Department
from app.services import faculty_service
import sqlalchemy as sa


def get_all():
    return db.session.execute(sa.select(Department)).scalars().all()

def get_by_id(id: int) :
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
