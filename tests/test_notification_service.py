import os
import unittest
from datetime import datetime

from tests.test_config import TestConfig
from app.dto.notification_dto import NotificationDTO
from app.services import user_service, notification_service
from app.dto.user_dto import UserDTO
from app.models import user
from app import create_app, db


os.environ['DATABASE_URL'] = 'sqlite://'


class FacultyServiceCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
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
        self.app.logger.info('Запуск тестирования отправки уведомления')
        notificationDTO = NotificationDTO(message='test', user_id=self.user.id)
        notification_service.send_message(notificationDTO)
        created_notification = notification_service.get_by_id(1)
        res = user_service.get_notifications(1, True, self.user).items
        self.app.logger.info(res)
        self.assertTrue(
            len(res) == 1 and res[0].message == notificationDTO.message)
        self.assertTrue(
            created_notification is not None and created_notification.message == notificationDTO.message)
        self.assertTrue(created_notification.time_sent.date()
                        == datetime.now().date())

    def test_notification_count(self):
        self.app.logger.info('Запуск тестирования количества уведомлений')
        self.create_notifications()
        self.assertEqual(
            notification_service.get_user_notifications_count(self.user.id), 3)
        notification_service.read_message(1)
        self.assertEqual(
            notification_service.get_user_notifications_count(self.user.id), 2)

    def test_read(self):
        self.app.logger.info('Запуск тестирования чтения уведомления')
        self.create_notifications()
        notification_service.read_message(1)
        created_notification = notification_service.get_by_id(1)
        self.assertTrue(created_notification.has_read == True)
        self.assertTrue(len(user_service.get_notifications(
            1, True, user=self.user).items) == 2)
        self.assertTrue(len(user_service.get_notifications(
            1, False, user=self.user).items) == 3)

    def test_delete(self):
        self.app.logger.info('Запуск тестирования удаления уведомления')
        self.create_notifications()
        notification = notification_service.get_by_id(1)
        notification_service.delete(notification.id)
        with self.assertRaises(ValueError):
            notification = notification_service.get_by_id(1)
        self.assertTrue(len(user_service.get_notifications(
            1, False, self.user).items) == 2)


if __name__ == '__main__':
    unittest.main(verbosity=2)
