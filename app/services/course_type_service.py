from app import db
from app.dto.course_type_dto import CourseTypeDTO
from app.models.course_type import CourseType, add_years
import sqlalchemy as sa
from datetime import datetime


def get_all():
    return db.session.execute(sa.select(CourseType)).scalars().all()


def get_by_id(id: int):
    return db.session.get(CourseType, id)


def get_by_name(name: str):
    return db.session.execute(sa.select(CourseType).where(CourseType.name == name)).scalar_one_or_none()


def create(course_typeDTO: CourseTypeDTO):
    course_type = CourseType(name=course_typeDTO.name,
                             deadline=add_years(datetime.now(), 3))
    db.session.add(course_type)
    db.session.commit()
    return True


def update(course_typeDTO: CourseTypeDTO):
    record = get_by_id(course_typeDTO.id)
    if record is None:
        return False
    if course_typeDTO.name is not None:
        record.name = course_typeDTO.name
    db.session.commit()
    return True


def delete(id: int) -> bool:
    course_type = get_by_id(id)
    if (course_type is None):
        return False
    db.session.delete(course_type)
    db.session.commit()
    return True


def update_deadline(course_typeDTO: CourseTypeDTO):
    record = None
    if (course_typeDTO.id is not None):
        record = get_by_id(course_typeDTO.id)
    else:
        record = get_by_name(course_typeDTO.name)
    record.deadline = add_years(record.deadline, 3)
    db.session.commit()
