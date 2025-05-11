import os
os.environ['DATABASE_URL'] = 'sqlite://'

from datetime import datetime, timezone
from sqlite3 import DataError
from app.dto.notification_dto import NotificationDTO
from sqlalchemy.exc import IntegrityError
from app.services import user_service, notification_service
from app.dto.user_dto import UserDTO
from app.models import user
from app import app, db
import unittest

class FacultyServiceCase(unittest.TestCase):
    def setUp(self):
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()
        user_service.create(userDTO=UserDTO(
            username='Test User', full_name='Tester tester test', password='test', role=user.TEACHER))
        self.user = user_service.get_by_id(1)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def create_notifications(self):
        test_notifications = [
            NotificationDTO(message='message1', user_id=self.user.id),
            NotificationDTO(message='message2', user_id=self.user.id),
            NotificationDTO(message='message3', user_id=self.user.id)
        ]
        for notification in test_notifications:
            notification_service.send_message(notification)

    def test_send(self):
        app.logger.info('Запуск тестирования отправки уведомления')
        notificationDTO = NotificationDTO(message='test', user_id=self.user.id)
        notification_service.send_message(notificationDTO)
        created_notification = notification_service.get_by_id(1)
        res = user_service.get_notifications(1, True, self.user).items
        app.logger.info(res)
        self.assertTrue(
            len(res) == 1 and res[0].message == notificationDTO.message)
        self.assertTrue(
            created_notification is not None and created_notification.message == notificationDTO.message)
        self.assertTrue(created_notification.time_sent.date()
                        == datetime.now(timezone.utc).date())

    def test_read(self):
        app.logger.info('Запуск тестирования чтения уведомления')
        self.create_notifications()
        notification_service.read_message(1)
        created_notification = notification_service.get_by_id(1)
        self.assertTrue(created_notification.has_read == True)
        self.assertTrue(len(user_service.get_notifications(1, True, user=self.user).items) == 2)
        self.assertTrue(len(user_service.get_notifications(1, False, user=self.user).items) == 3)

    def test_delete(self):
        app.logger.info('Запуск тестирования удаления уведомления')
        self.create_notifications()
        notification = notification_service.get_by_id(1)
        notification_service.delete(notification.id)
        with self.assertRaises(ValueError):
            notification = notification_service.get_by_id(1)
        self.assertTrue(len(user_service.get_notifications(1, False, self.user).items) == 2)


if __name__ == '__main__':
    unittest.main(verbosity=2)
