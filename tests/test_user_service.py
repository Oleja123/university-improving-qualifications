import os
os.environ['DATABASE_URL'] = 'sqlite://'

import unittest
from app import app, db
from app.dto.department_dto import DepartmentDTO
from app.dto.faculty_dto import FacultyDTO
from app.dto.notification_dto import NotificationDTO
from app.dto.user_dto import UserDTO
from app.exceptions.wrong_password_error import WrongPasswordError
from app.services import department_service, faculty_service, user_service, notification_service
from werkzeug.security import generate_password_hash
import sqlalchemy as sa
from app.models.user import TEACHER, ADMIN

class UserServiceTestCase(unittest.TestCase):
    def setUp(self):
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()

        faculty_service.create(FacultyDTO(name='test faculty'))
        self.faculty = faculty_service.get_by_name('test faculty')
        department_service.create(DepartmentDTO(faculty_id=self.faculty.id, name='test department'))
        self.department = department_service.get_by_name('test department')

        self.user_data = {
            'username': 'testuser',
            'full_name': 'Test User',
            'password': 'secure123',
            'role': 'student'
        }

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_create(self):
        app.logger.info('Запуск тестирования создания пользователя')
        dto = UserDTO(**self.user_data)
        user_service.create(dto)
        user = user_service.get_by_username('testuser')
        self.assertEqual(user.full_name, 'Test User')
        self.assertTrue(user_service.check_password_hash(
            user.password_hash, 'secure123'))

    def test_create_duplicate_username(self):
        app.logger.info(
            'Запуск тестирования создания пользователя с существующим именем')
        user_service.create(UserDTO(**self.user_data))
        with self.assertRaises(ValueError):
            user_service.create(UserDTO(**self.user_data))

    def test_check_password(self):
        app.logger.info(
            'Запуск тестирования создания пользователя с существующим именем')
        user_service.create(UserDTO(**self.user_data))
        with self.assertRaises(WrongPasswordError):
            user_service.check_password('testuser', 'wrongpass')

    def test_update_user(self):
        app.logger.info('Запуск тестирования обновления данных пользователя')
        user_service.create(UserDTO(**self.user_data))
        user = user_service.get_by_username('testuser')

        update_dto = UserDTO(
            id=user.id,
            username='updateduser',
            full_name='Updated Name',
            password='newpassword',
            role='teacher'
        )
        user_service.update(update_dto)

        updated = user_service.get_by_id(user.id)
        self.assertEqual(updated.username, 'updateduser')
        self.assertTrue(user_service.check_password(
            'updateduser', 'newpassword'))

    def test_delete_user(self):
        app.logger.info('Запуск тестирования удаления пользователя')
        user_service.create(UserDTO(**self.user_data))
        user = user_service.get_by_username('testuser')
        user_service.delete(user.id)
        with self.assertRaises(ValueError):
            user_service.get_by_id(user.id)

    def test_get_notifications(self):
        app.logger.info('Запуск теста получения уведомлений пользователя')
        user_service.create(UserDTO(**self.user_data))
        user = user_service.get_by_username('testuser')
        notification_service.send_message(
            NotificationDTO(user_id=user.id, message='Hello'))
        notifications = user_service.get_notifications(1, False, user)
        self.assertEqual(notifications.total, 1)
        self.assertEqual(notifications.items[0].message, 'Hello')

    def test_add_to_department(self):
        teacher_data = {
            'username': 'teacher1',
            'full_name': 'Teacher One',
            'password': 'teacher123',
            'role': TEACHER
        }
        user_service.create(UserDTO(**teacher_data))
        teacher = user_service.get_by_username('teacher1')

        user_service.add_to_department(teacher.id, self.department.id)

        teacher = user_service.get_by_id(teacher.id)
        self.assertIn(self.department, user_service.get_departments(UserDTO(id=teacher.id)))


    def test_add_to_department_non_teacher(self):
        admin_data = {
            'username': 'admin',
            'full_name': 'Admin One',
            'password': 'admin123',
            'role': ADMIN
        }
        user_service.create(UserDTO(**admin_data))
        admin = user_service.get_by_username('admin')

        with self.assertRaises(ValueError) as context:
            user_service.add_to_department(admin.id, self.department.id)


    def test_add_to_department_invalid_department(self):
        teacher_data = {
            'username': 'teacher2',
            'full_name': 'Teacher Two',
            'password': 'teacher123',
            'role': TEACHER
        }
        teacher = user_service.create(UserDTO(**teacher_data))

        with self.assertRaises(Exception) as context:
            user_service.add_to_department(teacher.id, 999)


if __name__ == '__main__':
    unittest.main(verbosity=2)
