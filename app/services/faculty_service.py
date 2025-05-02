from app import db
from app.models.faculty import Faculty
from app.dto.faculty_dto import FacultyDTO
import sqlalchemy as sa


def get_all():
    return db.session.execute(sa.select(Faculty)).scalars().all()

def get_by_id(id: int) :
    return db.session.get(Faculty, id)

def get_by_name(name: str):
    return db.session.execute(sa.select(Faculty).where(Faculty.name == name)).scalar_one_or_none()

def create(facultyDTO: FacultyDTO):
    faculty = Faculty(name = facultyDTO.name)
    db.session.add(faculty)
    db.session.commit()

def update(facultyDTO: FacultyDTO):
    record = get_by_id(facultyDTO.id)
    if record is None:
        return False
    record.name = facultyDTO.name
    db.session.commit()
    return True

def delete(id: int) -> bool:
    faculty = get_by_id(id)
    if (faculty is None):
        return False
    db.session.delete(faculty)
    db.session.commit()
    return True

def get_departments(facultyDTO: FacultyDTO):
    faculty = None
    if facultyDTO.id is not None:
        faculty = get_by_id(facultyDTO.id)
    else:
        faculty = get_by_name(facultyDTO.name)
    return db.session.scalars(faculty.departments.select()).all()


