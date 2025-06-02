import os
import unittest

from tests.test_config import TestConfig

from app import create_app, db
from app.services import course_type_service
from app.dto.course_type_dto import CourseTypeDTO


os.environ['DATABASE_URL'] = 'sqlite://'


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


if __name__ == '__main__':
    unittest.main(verbosity=2)
