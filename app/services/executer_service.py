from datetime import datetime

from flask import current_app

from app.interfaces.iexecuter import IExecuter
import sqlalchemy as sa

from app.models.course import Course
from app.models.course_type import CourseType
from app.models.user import User, TEACHER
from app import db
from app.services import sertificate_service, user_service


class Executer(IExecuter):

    def execute(self):
        try:
            current_app.logger.info('Запуск планировщика')
            timing = datetime.now()
            query = sa.select(User, CourseType, Course).join(Course).where(sa.and_(Course.is_included == True,
                                                                                User.is_fired == False,
                                                                                User.role == TEACHER))
            combs = db.session.execute(query).all()
            to_ban = set()
            for user, course_type, course in combs:
                res = sertificate_service.get(user.id, course.id)
                if (res.date_approved is None and course_type.deadline < timing) or res.date_approved > course_type.deadline:
                    to_ban.add(user.id)
            for user_id in to_ban:
                user_service.fire(user_id)
            current_app.logger.info(f"Заблокированные пользователи: {to_ban}")
        except Exception as e:
            current_app.logger.error(e)
            raise RuntimeError('Ошибка при выполненнии работы планировщика')
