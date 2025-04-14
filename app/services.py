from app.forms import EditFacultyForm, EditDepartmentForm, EditCourseTypeForm, EditCourseForm
from app.models import Faculty, Department, CourseType, Course
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


class TypeService:

    @staticmethod
    def get_by_id(id: int) -> CourseType:
        return db.session.get(CourseType, id)

    @staticmethod
    def get_by_name(name: str) -> CourseType:
        return db.session.scalar(
            sa.select(CourseType).where(CourseType.name == name))

    @staticmethod
    def get_all() -> list[CourseType]:
        return db.session.scalars(sa.select(CourseType).order_by(CourseType.name)).all()

    @staticmethod
    def create(form: EditCourseTypeForm) -> CourseType:
        course_type = CourseType.from_form(form)
        db.session.add(course_type)
        db.session.commit()
        return course_type

    @staticmethod
    def edit(id: int, form: EditCourseTypeForm) -> CourseType:
        course_type = TypeService.get_by_id(id)
        if course_type is None:
            return None
        course_type.name = form.name.data
        db.session.commit()
        return course_type

    @staticmethod
    def delete(id: int) -> bool:
        course_type = db.session.get(CourseType, id)
        if course_type is None:
            return False
        db.session.delete(course_type)
        db.session.commit()
        return True
    

class CourseService:

    @staticmethod
    def get_by_id(id: int) -> Course:
        return db.session.get(Course, id)

    @staticmethod
    def get_by_name(name: str) -> Course:
        return db.session.scalar(
            sa.select(Course).where(Course.name == name))

    @staticmethod
    def get_all() -> list[Course]:
        return db.session.scalars(sa.select(Course).order_by(Course.name)).all()

    @staticmethod
    def create(form: EditCourseForm) -> Course:
        type = TypeService.get_by_id(form.type.data)
        course = Course.from_form(form, type)
        db.session.add(course)
        db.session.commit()
        return course

    @staticmethod
    def edit(id: int, form: EditCourseForm) -> Course:
        course = CourseService.get_by_id(id)
        if course is None:
            return None
        course.name = form.name.data
        type = TypeService.get_by_id(form.type.data)
        course.faculty = type
        db.session.commit()
        return course

    @staticmethod
    def delete(id: int) -> bool:
        course = db.session.get(Course, id)
        if course is None:
            return False
        db.session.delete(course)
        db.session.commit()
        return True

