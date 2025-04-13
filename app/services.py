from app.forms import EditFacultyForm, EditDepartmentForm
from app.models import Faculty, Department
import sqlalchemy as sa
from app import db


class FacultyService:

    @staticmethod
    def get_by_id(id: int) -> Faculty:
        return db.session.get(Faculty, id)

    @staticmethod
    def get_by_name(name: str) -> Faculty:
        return db.session.scalar(
            sa.select(Faculty).where(Faculty.name == name))

    @staticmethod
    def get_all() -> list[Faculty]:
        return db.session.scalars(sa.select(Faculty).order_by(Faculty.name)).all()

    @staticmethod
    def create(form: EditFacultyForm) -> Faculty:
        faculty = Faculty.from_form(form)
        db.session.add(faculty)
        db.session.commit()
        return faculty

    @staticmethod
    def edit(id: int, form: EditFacultyForm) -> Faculty:
        faculty = FacultyService.get_by_id(id)
        if faculty is None:
            return None
        faculty.name = form.name.data
        db.session.commit()
        return faculty

    @staticmethod
    def delete(id: int) -> bool:
        faculty = FacultyService.get_by_id(id)
        if (faculty is None):
            return False
        db.session.delete(faculty)
        db.session.commit()
        return True


class DepartmentService:

    @staticmethod
    def get_by_id(id: int) -> Department:
        return db.session.get(Department, id)

    @staticmethod
    def get_by_name(name: str) -> Department:
        return db.session.scalar(
            sa.select(Department).where(Department.name == name))

    @staticmethod
    def get_all() -> list[Department]:
        return db.session.scalars(sa.select(Department).order_by(Department.name)).all()

    @staticmethod
    def create(form: EditDepartmentForm) -> Department:
        faculty = FacultyService.get_by_id(form.faculty.data)
        department = Department.from_form(form, faculty)
        db.session.add(department)
        db.session.commit()
        return department

    @staticmethod
    def edit(id: int, form: EditDepartmentForm) -> Department:
        department = DepartmentService.get_by_id(id)
        if department is None:
            return None
        department.name = form.name.data
        faculty = FacultyService.get_by_id(form.faculty.data)
        department.faculty = faculty
        db.session.commit()
        return department

    @staticmethod
    def delete(id: int) -> bool:
        department = db.session.get(Department, id)
        if department is None:
            return False
        db.session.delete(department)
        db.session.commit()
        return True
