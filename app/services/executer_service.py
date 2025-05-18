from datetime import datetime, timedelta

from flask import current_app

from app.dto.notification_dto import NotificationDTO
from app.interfaces.iexecuter import IExecuter
import sqlalchemy as sa

from app.models.course import Course
from app.models.course_type import CourseType
from app.models.user import User, TEACHER
from app import db
from app.services import notification_service, sertificate_service, user_service


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
                elif not res.date_approved:
                    try:
                        delta = course_type.deadline - timing
                        if delta < timedelta(days=30):
                            notification_service.send_message(NotificationDTO(user_id=user.id,
                                                                              message=f'Осталось {delta.days} чтобы пройти курс {course.name}'))
                    except Exception as e:
                        current_app.logger.info(
                            'Не удалось отправить сообщение пользователю {user.id}')
            for user_id in to_ban:
                try:
                    user_service.fire(user_id)
                    user_service.close_user_session(user_id)
                except Exception as e:
                    current_app.logger.info(
                        'Не удалось закрыть сессии пользователя {user_id}')
            current_app.logger.info(f"Заблокированные пользователи: {to_ban}")
        except Exception as e:
            current_app.logger.error(e)
            raise RuntimeError('Ошибка при выполненнии работы планировщика')
