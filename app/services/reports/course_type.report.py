from datetime import datetime
from app.models import course_type
from app.models.course import Course
from app.models.department import Department
from app.models.teacher_course import TeacherCourse
from app.models.user import User
import sqlalchemy as sa
from app import db
from app.services import course_type_service


class CourseTypeReport:

    def __init__(self, course_type_id, date_from:datetime = None, date_to:datetime = None):
        self.course_type = course_type_service.get_by_id(course_type_id)
        self.course_type_name = self.course_type.name
        self.table_header = ['ФИО преподавателя', 'Имя пользователя', 'Название курса', 'Дата подтверждения']
        query = (sa.select(
            User.full_name,
            User.username, 
            Course.name, 
            TeacherCourse.date_approved
        )
        .join(User.courses)
        .join(User.departments)
        .join(TeacherCourse.course)
        .where(sa.and_(
            Course.course_type_id == course_type_id, 
            TeacherCourse.date_approved.is_not(None),
            sa.or_(
                date_from is None,
                sa.func.date(TeacherCourse.date_approved) >= date_from
            ),
            sa.or_(
                date_to is None,
                sa.func.date(TeacherCourse.date_approved) <= date_to,
            ),
            User.is_fired == False
            ))
        .distinct()
        .order_by(sa.desc(TeacherCourse.date_approved)))
        self.rows = db.session.execute(query).all()
        self.result = len(self.rows)