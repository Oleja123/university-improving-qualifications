import os
import unittest

from tests.test_config import TestConfig
from app import create_app, db
from app.services import course_service, course_type_service
from app.dto.course_dto import CourseDTO
from app.dto.course_type_dto import CourseTypeDTO


os.environ['DATABASE_URL'] = 'sqlite://'


class CourseServiceCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        course_type_service.create(
            CourseTypeDTO(name='Programming'))
        self.course_type = course_type_service.get_by_name('Programming')

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def create_courses(self):
        test_courses = [
            CourseDTO(name='Python Basics',
                      course_type_id=self.course_type.id),
            CourseDTO(name='Web Development',
                      course_type_id=self.course_type.id),
            CourseDTO(name='Data Science', course_type_id=self.course_type.id)
        ]
        for course in test_courses:
            course_service.create(course)

    def test_create(self):
        self.app.logger.info('Запуск тестирования создания курса')
        courseDTO = CourseDTO(
            name='Algorithms', course_type_id=self.course_type.id)
        course_service.create(courseDTO)
        created_course = course_service.get_by_name(courseDTO.name)
        self.assertTrue(
            created_course is not None and
            courseDTO.name == created_course.name and
            courseDTO.course_type_id == created_course.course_type_id
        )

    def test_update(self):
        self.app.logger.info('Запуск тестирования обновления курса')
        self.create_courses()
        course = course_service.get_by_name('Web Development')
        new_name = 'Advanced Web Development'
        courseDTO = CourseDTO(id=course.id, name=new_name,
                              course_type_id=self.course_type.id)
        course_service.update(courseDTO)
        updated_course = course_service.get_by_id(course.id)
        self.assertTrue(
            updated_course is not None and updated_course.name == new_name)

    def test_delete(self):
        self.app.logger.info('Запуск тестирования удаления курса')
        self.create_courses()
        course = course_service.get_by_name('Data Science')
        course_service.delete(course.id)
        with self.assertRaises(ValueError):
            course_service.get_by_id(course.id)

    def test_get_all_paginated(self):
        self.app.logger.info('Запуск тестирования пагинации курсов')
        self.create_courses()
        page = course_service.get_all_paginated(page=1)
        self.assertEqual(page.total, 3)

    def test_same_name_create(self):
        self.app.logger.info(
            'Запуск тестирования создания курса с одинаковым именем')
        self.create_courses()
        with self.assertRaises(ValueError):
            courseDTO = CourseDTO(name='Python Basics',
                                  course_type_id=self.course_type.id)
            course_service.create(courseDTO)

    def test_get_by_id_nonexistent(self):
        self.app.logger.info(
            'Запуск тестирования получения несуществующего курса по ID')
        with self.assertRaises(ValueError):
            course_service.get_by_id(999)

    def test_get_by_name_nonexistent(self):
        self.app.logger.info(
            'Запуск тестирования получения несуществующего курса по имени')
        with self.assertRaises(ValueError):
            course_service.get_by_name('Non_Existent_Course')

    def test_create_without_course_type(self):
        self.app.logger.info('Запуск тестирования создания курса без типа')
        with self.assertRaises(ValueError):
            courseDTO = CourseDTO(name='Invalid Course')
            course_service.create(courseDTO)


if __name__ == '__main__':
    unittest.main(verbosity=2)
