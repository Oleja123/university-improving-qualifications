import os

from app.dto.user_dto import UserDTO

os.environ['DATABASE_URL'] = 'sqlite://'

from unittest.mock import MagicMock
from app.services.executer import Executer


from datetime import datetime, timedelta
from app.dto.notification_dto import NotificationDTO
from app.interfaces.iexecuter import IExecuter
from app.models import Course, TeacherCourse, User, CourseType
from app.services import course_service, user_service, notification_service
from app import app, db
import unittest

class ExecuterServiceCase(unittest.TestCase):
    def setUp(self):
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()
        
        self.course_type = CourseType(name="Test Type", deadline=datetime.now() + timedelta(days=15))
        self.course = Course(name="Test Course", is_included=True, course_type=self.course_type)
        
        user_service.create(UserDTO(username="user1", full_name="user1", role=1, password="aboba1"))
        user_service.create(UserDTO(username="user2", full_name="user2", role=1, password="aboba2"))

        self.user1 = User(username="user1", full_name="user1", passworis_fired=False)
        self.user2 = User(username="user2", is_fired=False)
        
        db.session.add_all([self.course_type, self.course, self.user1, self.user2])
        db.session.commit()
        
        self.original_course_service = course_service.get_all
        self.original_user_service = user_service.get_all
        self.original_fire = user_service.fire
        self.original_send_message = notification_service.send_message
        
        course_service.get_all = MagicMock(return_value=[self.course])
        user_service.get_all = MagicMock(return_value=[self.user1, self.user2])
        user_service.fire = MagicMock()
        notification_service.send_message = MagicMock()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        
        course_service.get_all = self.original_course_service
        user_service.get_all = self.original_user_service
        user_service.fire = self.original_fire
        notification_service.send_message = self.original_send_message

    def test_user_with_approved_course_not_notified(self):
        app.logger.info('Запуск теста: пользователь с одобренным курсом')
        
        tc = TeacherCourse(
            user_id=self.user1.id,
            course_id=self.course.id,
            date_approved=datetime.now()
        )
        db.session.add(tc)
        db.session.commit()
        
        executer = Executer()
        executer.execute()
        
        notification_service.send_message.assert_not_called()

    def test_user_without_course_gets_notification(self):
        app.logger.info('Запуск теста: уведомление пользователю без курса')
        
        executer = Executer()
        executer.execute()
        
        notification_service.send_message.assert_called()
        notification = notification_service.send_message.call_args[0][0]
        self.assertIsInstance(notification, NotificationDTO)
        self.assertEqual(notification.user_id, self.user1.id)
        self.assertIn(str((self.course.course_type.deadline - datetime.now()).days), notification.message)

    def test_user_fired_after_deadline(self):
        app.logger.info('Запуск теста: увольнение после дедлайна')
        
        self.course.course_type.deadline = datetime.now() - timedelta(days=1)
        db.session.commit()
        
        executer = Executer()
        executer.execute()
        
        user_service.fire.assert_called_with(self.user1.id)
        self.assertTrue(self.user1.is_fired)

    def test_user_not_fired_if_already_fired(self):
        app.logger.info('Запуск теста: проверка повторного увольнения')
        
        self.user1.is_fired = True
        db.session.commit()
        
        self.course.course_type.deadline = datetime.now() - timedelta(days=1)
        db.session.commit()
        
        executer = Executer()
        executer.execute()
        
        user_service.fire.assert_not_called()

    def test_notification_not_sent_if_more_than_30_days(self):
        app.logger.info('Запуск теста: проверка срока уведомления')
        
        self.course.course_type.deadline = datetime.now() + timedelta(days=31)
        db.session.commit()
        
        executer = Executer()
        executer.execute()
        
        notification_service.send_message.assert_not_called()

    def test_multiple_courses_handling(self):
        app.logger.info('Запуск теста: несколько курсов')
        
        course_type2 = CourseType(name="Type2", deadline=datetime.now() + timedelta(days=5))
        course2 = Course(name="Course 2", is_included=True, course_type=course_type2)
        db.session.add_all([course_type2, course2])
        db.session.commit()
        
        course_service.get_all = MagicMock(return_value=[self.course, course2])
        
        executer = Executer()
        executer.execute()
        
        self.assertEqual(notification_service.send_message.call_count, 4) 

    def test_included_courses_filter(self):
        app.logger.info('Запуск теста: фильтрация курсов')
        
        course_type2 = CourseType(name="Type2", deadline=datetime.now() + timedelta(days=5))
        course2 = Course(name="Course 2", is_included=False, course_type=course_type2)
        db.session.add_all([course_type2, course2])
        db.session.commit()
        
        executer = Executer()
        executer.execute()
        
        notification_service.send_message.assert_called()
        self.assertEqual(notification_service.send_message.call_count, 2) 

if __name__ == '__main__':
    unittest.main(verbosity=1)