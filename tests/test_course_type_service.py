import os

from tests.test_config import TestConfig
os.environ['DATABASE_URL'] = 'sqlite://'

from app.dto.course_type_dto import CourseTypeDTO
from app.services import course_type_service
from app import create_app, db
import unittest
from datetime import datetime


class CourseTypeServiceCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_add_years(self):
        test_date = datetime(2023, 2, 15)
        result = course_type_service.add_years(test_date, 2)
        self.assertEqual(result, datetime(2025, 2, 15))
        
        leap_date = datetime(2020, 2, 29)
        result = course_type_service.add_years(leap_date, 1)
        self.assertEqual(result, datetime(2021, 2, 28))

    def create_course_types(self):
        test_course_types = [
            CourseTypeDTO(name='Bebra'),
            CourseTypeDTO(name='aboba'),
            CourseTypeDTO(name='boba')
        ]
        for course_type in test_course_types:
            course_type_service.create(course_type)

    def test_create(self):
        self.app.logger.info('Запуск теста создания типа курсов')
        course_typeDTO = CourseTypeDTO(name='Test Course Type')
        course_type_service.create(course_typeDTO)
        created = course_type_service.get_by_name(course_typeDTO.name)
        self.assertEqual(created.name, 'Test Course Type')

    def test_update(self):
        self.app.logger.info('Запуск тестирования обновления типов курсов')
        course_typeDTO = CourseTypeDTO(name='Test Course Type')
        course_type_service.create(course_typeDTO)
        created = course_type_service.get_by_name(course_typeDTO.name)
        course_type_service.update(
            CourseTypeDTO(id=created.id, name='New name'))
        course_type = course_type_service.get_by_id(created.id)
        self.assertEqual(course_type.name, 'New name')

    def test_delete(self):
        self.app.logger.info('Запуск тестирования удаления типа курсов')
        course_typeDTO = CourseTypeDTO(name='Test Course Type')
        course_type_service.create(course_typeDTO)
        created = course_type_service.get_by_name(course_typeDTO.name)
        course_type_service.delete(created.id)
        with self.assertRaises(ValueError):
            course_type = course_type_service.get_by_id(created.id)


    def test_get_all(self):
        self.app.logger.info('Запуск получения всех типов курсов')
        self.create_course_types()
        self.assertTrue(len(course_type_service.get_all()) == 3)

    def test_get_all_empty(self):
        self.app.logger.info(
            'Запуск теста получения всех типов курсов из пустой БД')
        self.assertEqual(len(course_type_service.get_all()), 0)

    def test_date(self):
        fixed_time = datetime.now()

        dto = CourseTypeDTO(name="Computer Science")
        course_type_service.create(dto)

        created = course_type_service.get_by_name("Computer Science")
        self.assertEqual(datetime.date(created.deadline), datetime.date(course_type_service.add_years(fixed_time, 3)))


if __name__ == '__main__':
    unittest.main(verbosity=2)
