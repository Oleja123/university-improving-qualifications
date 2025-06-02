from datetime import datetime

import sqlalchemy as sa

from app.models.course import Course
from app.models.teacher_course import TeacherCourse
from app.models.user import User
from app import db
from app.services import course_type_service


class CourseTypeReport:

    def __init__(self, course_type_id, date_from: datetime = None, date_to: datetime = None):
        self.date_from = f"От: {date_from.isoformat()}"
        self.date_to = f"До: {date_to.isoformat()}"
        self.course_type = course_type_service.get_by_id(course_type_id)
        self.filter_item_name = self.course_type.name
        self.table_header = ['ФИО преподавателя', 'Имя пользователя',
                             'Название курса', 'Дата подтверждения', '№ Подтверждающего документа']
        query = (sa.select(
            User.full_name,
            User.username,
            Course.name,
            TeacherCourse.date_completion,
            TeacherCourse.confirming_document,
        )
            .join(User.courses)
            .outerjoin(User.departments)
            .join(TeacherCourse.course)
            .where(sa.and_(
                Course.course_type_id == course_type_id,
                TeacherCourse.date_completion.is_not(None),
                sa.or_(
                    date_from is None,
                    TeacherCourse.date_completion >= date_from
                ),
                sa.or_(
                    date_to is None,
                    TeacherCourse.date_completion <= date_to,
                ),
            ))
            .distinct()
            .order_by(sa.desc(TeacherCourse.date_completion)))
        self.rows = db.session.execute(query).all()
        self.result = len(self.rows)
        subquery = (sa.select(
            User.full_name,
            User.username,
            Course.name,
            TeacherCourse.date_completion,
            TeacherCourse.confirming_document,
        )
            .join(User.courses)
            .outerjoin(User.departments)
            .join(TeacherCourse.course)
            .where(sa.and_(
                Course.course_type_id == course_type_id,
                TeacherCourse.date_completion.is_not(None)
            )
        ).distinct().subquery())
        query = sa.select(sa.func.count()).select_from(subquery)
        delim = db.session.scalar(query)
        if delim == 0:
            self.percent = ''
        else:
            self.percent = f"{len(self.rows) / db.session.scalar(query) * 100:.2f}%"
        self.percent_target = 'Процент пройденных преподавателями курсов заданного типа за данный период ' \
            'по отношению ко всем пройденным преподавателями курсам заданного типа'
