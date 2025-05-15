from datetime import datetime

from flask import current_app
from app.dto.notification_dto import NotificationDTO
from app.dto.user_dto import UserDTO
from app.interfaces.iexecuter import IExecuter
import sqlalchemy as sa
from app import db, app

from app.models.course import Course
from app.models.teacher_course import TeacherCourse
from app.services import course_service, notification_service, user_service
from app.models.user import TEACHER

class Executer(IExecuter):
    def execute(self):
        courses = course_service.get_all(included=True)
        users = user_service.get_all(UserDTO(role=TEACHER))
        for course in courses:
            for user in users:
                is_found = False
                user_courses = db.session.scalars(user.courses.select().where(sa.and_(TeacherCourse.date_approved.is_not(None),
                    TeacherCourse.date_approved <= course.course_type.deadline, TeacherCourse.course.is_included == True))).all()
                for user_course in  user_courses:
                    if user_course.course_id == course.id:
                        is_found = True
                        break
                if not is_found:
                    current_app.logger.info('Пользователь {user.username} не прошел проверку на прохождение курса {course.name}')
                    current_time = datetime.now()
                    if current_time <= course.course_type.deadline:
                        date_dif = course.course_type.deadline - current_time
                        date_dif = date_dif.days
                        if date_dif <= 30:
                            current_app.logger.info(f"Пользователю {user.username} отправлено уведомление")
                            msg = f"До окончания принятия заявок по курсу {course.name} осталось {date_dif} дней. Поспешите!!!"
                            notification_service.send_message(NotificationDTO(user_id=user.id, message=msg))
                    else:
                        if not user.is_fired:
                            current_app.logger.info(f"Пользователь {user.username} уволен")
                        user_service.fire(user.id)
                        user.is_fired = True
                else:
                    current_app.logger.info('Пользователь {user.username} успешно прошел проверку на прохождение курса {course.name}')