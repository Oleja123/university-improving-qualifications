from datetime import datetime

from app.models.course import Course
from app.models.department import Department
from app.models.teacher_course import TeacherCourse
from app.models.user import User
from app.services import faculty_service
import sqlalchemy as sa
from app import db


class FacultyReport:

    def __init__(self, faculty_id, date_from:datetime = None, date_to:datetime = None):
        self.faculty = faculty_service.get_by_id(faculty_id)
        self.filter_item_name = self.faculty.name
        self.table_header = ['ФИО преподавателя', 'Имя пользователя', 'Название курса', 'Дата подтверждения']
        query = (sa.select(
            User.full_name,
            User.username, 
            Course.name, 
            TeacherCourse.date_completion
        )
        .join(User.courses)
        .join(User.departments)
        .join(TeacherCourse.course)
        .where(sa.and_(
            Department.faculty_id == faculty_id, 
            TeacherCourse.date_completion.is_not(None),
            sa.or_(
                date_from is None,
                TeacherCourse.date_completion >= date_from
            ),
            sa.or_(
                date_to is None,
                TeacherCourse.date_completion <= date_to,
            ),
            User.is_fired == False
            ))
        .distinct()
        .order_by(sa.desc(TeacherCourse.date_completion)))
        self.rows = db.session.execute(query).all()
        self.result = len(self.rows)