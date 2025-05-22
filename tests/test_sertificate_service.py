import os

from tests.test_config import TestConfig
os.environ['DATABASE_URL'] = 'sqlite://'

from app.dto.course_dto import CourseDTO
from app.dto.course_type_dto import CourseTypeDTO
from app.dto.user_dto import UserDTO
from app.models import user
from app.services import course_service, course_type_service, sertificate_service, user_service
from app import create_app, db
import unittest


class SertificateServiceTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        user_service.create(UserDTO(username='test_user', password='test_password', role=user.TEACHER, full_name='Tester'))
        self.user = user_service.get_by_username('test_user')
        course_type_service.create(CourseTypeDTO(name='test_course_type'))
        self.course_type = course_type_service.get_by_name('test_course_type')

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def create_courses(self):
        test_courses = [
            CourseDTO(name='test_course1', course_type_id=self.course_type.id),
            CourseDTO(name='test_course2', course_type_id=self.course_type.id),
            CourseDTO(name='test_course3', course_type_id=self.course_type.id)
        ]
        for course in test_courses:
            course_service.create(course)


    def test_get_zero_approved(self):
        self.create_courses()
        self.assertEqual(len(sertificate_service.get_user_courses(self.user.id, 1).items), 0)

    def test_get_approved(self):
        self.create_courses()
        sertificate_service.approve_user_course(self.user.id, 1)
        self.assertEqual(len(sertificate_service.get_user_courses(self.user.id, 1, approved=True).items), 1)
        self.assertEqual(len(sertificate_service.get_user_courses(self.user.id, 1, approved=False).items), 0)
        sertificate_service.get(self.user.id, 2)
        sertificate_service.get(self.user.id, 3)
        self.assertEqual(len(sertificate_service.get_user_courses(self.user.id, 1, approved=True).items), 1)
        self.assertEqual(len(sertificate_service.get_user_courses(self.user.id, 1, approved=False).items), 2)
        self.assertEqual(len(sertificate_service.get_user_courses(self.user.id, 1).items), 3)

    def test_several_users(self):
        self.create_courses()
        user_service.create(UserDTO(username='test_user2', password='test_password', role=user.TEACHER, full_name='Tester2'))
        user2 = user_service.get_by_username('test_user2')
        sertificate_service.approve_user_course(self.user.id, 1)
        self.assertEqual(len(sertificate_service.get_user_courses(self.user.id, 1, approved=True).items), 1)
        self.assertEqual(len(sertificate_service.get_user_courses(self.user.id, 1, approved=False).items), 0)
        self.assertEqual(len(sertificate_service.get_user_courses(user2.id, 1).items), 0)
        sertificate_service.approve_user_course(user2.id, 1)
        sertificate_service.approve_user_course(user2.id, 2)
        sertificate_service.get(user2.id, 3)
        self.assertEqual(len(sertificate_service.get_user_courses(user2.id, 1, approved=True).items), 2)
        self.assertEqual(len(sertificate_service.get_user_courses(user2.id, 1, approved=False).items), 1)


if __name__ == '__main__':
    unittest.main(verbosity=2)
