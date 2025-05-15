from app import db, app
from app.models.faculty import Faculty
from app.dto.faculty_dto import FacultyDTO
import sqlalchemy as sa


def get_all():
    try:
        return db.session.execute(sa.select(Faculty).order_by(Faculty.name)).scalars().all()
    except Exception as e:
        db.session.rollback()
        app.logger.error(e)
        raise Exception('Неизвестная ошибка')

def get_by_id(id: int) :
    try:
        res = db.session.get(Faculty, id)
        if res is None:
            raise ValueError(f'Факультет с id = {id} не существует')
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
        res = db.session.execute(sa.select(Faculty).where(Faculty.name == name)).scalar_one_or_none()
        if res is None:
            raise ValueError(f'Факультет с именем {name} не существует')
        return res
    except ValueError as e:
        db.session.rollback()
        app.logger.error(e)
        raise
    except Exception as e:
        db.session.rollback()
        app.logger.error(e)
        raise Exception(f'Неизвестная ошибка')

def create(facultyDTO: FacultyDTO):
    try:
        faculty = Faculty(name = facultyDTO.name)
        db.session.add(faculty)
        db.session.commit()
    except sa.exc.IntegrityError as e:
        db.session.rollback()
        app.logger.error(e)
        raise ValueError(f'Факультет с именем {facultyDTO.name} уже существует')
    except Exception as e:
        db.session.rollback()
        app.logger.error(e)
        raise Exception(f'Неизвестная ошибка при создании факультета')
    

def update(facultyDTO: FacultyDTO):
    try:
        record = get_by_id(facultyDTO.id)
        record.name = facultyDTO.name
        db.session.commit()
    except ValueError:
        raise
    except sa.exc.IntegrityError as e:
        db.session.rollback()
        app.logger.error(e)
        raise ValueError(f'Факультет с именем {facultyDTO.name} уже существует')
    except Exception as e:
        db.session.rollback()
        app.logger.error(e)
        raise Exception(f'Неизвестная ошибка при обновлении факультета')
    

def delete(id: int) -> bool:
    try:
        faculty = get_by_id(id)
        db.session.delete(faculty)
        db.session.commit()
    except ValueError:
        raise
    except Exception as e:
        db.session.rollback()
        app.logger.error(e)
        raise Exception(f'Неизвестная ошибка при удалении факультета')

def get_departments(facultyDTO: FacultyDTO):
    try:
        faculty = None
        if facultyDTO.id is not None:
            faculty = get_by_id(facultyDTO.id)
        else:
            faculty = get_by_name(facultyDTO.name)
        return db.session.scalars(faculty.departments.select()).all()
    except ValueError:
        raise
    except Exception as e:
        db.session.rollback()
        app.logger.error(e)
        raise Exception(f'Неизвестная ошибка при получении факультетов')


