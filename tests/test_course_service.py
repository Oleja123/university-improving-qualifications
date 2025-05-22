import os

from tests.test_config import TestConfig
os.environ['DATABASE_URL'] = 'sqlite://'

from app.dto.course_type_dto import CourseTypeDTO
from app.dto.course_dto import CourseDTO
from app.services import course_service, course_type_service
from app import create_app, db
import unittest


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
            CourseDTO(name='Python Basics', course_type_id=self.course_type.id),
            CourseDTO(name='Web Development', course_type_id=self.course_type.id),
            CourseDTO(name='Data Science', course_type_id=self.course_type.id)
        ]
        for course in test_courses:
            course_service.create(course)

    def test_create(self):
        self.app.logger.info('Запуск тестирования создания курса')
        courseDTO = CourseDTO(name='Algorithms', course_type_id=self.course_type.id)
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
        courseDTO = CourseDTO(id=course.id, name=new_name, course_type_id=self.course_type.id)
        course_service.update(courseDTO)
        updated_course = course_service.get_by_id(course.id)
        self.assertTrue(updated_course is not None and updated_course.name == new_name)

    def test_delete(self):
        self.app.logger.info('Запуск тестирования удаления курса')
        self.create_courses()
        course = course_service.get_by_name('Data Science')
        course_service.delete(course.id)
        with self.assertRaises(ValueError):
            course_service.get_by_id(course.id)

    def test_get_all(self):
        self.app.logger.info('Запуск тестирования получения всех курсов')
        self.create_courses()
        courses = course_service.get_all()
        self.assertEqual(len(courses), 3)
        self.assertEqual(courses[0].name, 'Python Basics')

    def test_get_all_paginated(self):
        self.app.logger.info('Запуск тестирования пагинации курсов')
        self.create_courses()
        page = course_service.get_all_paginated(page=1)
        self.assertEqual(page.total, 3)

    def test_same_name_create(self):
        self.app.logger.info('Запуск тестирования создания курса с одинаковым именем')
        self.create_courses()
        with self.assertRaises(ValueError):
            courseDTO = CourseDTO(name='Python Basics', course_type_id=self.course_type.id)
            course_service.create(courseDTO)

    def test_change_included(self):
        self.app.logger.info('Запуск тестирования изменения флага included')
        self.create_courses()
        course = course_service.get_by_name('Python Basics')
        initial_state = course.is_included
        course_service.change_included(course.id)
        changed_course = course_service.get_by_id(course.id)
        self.assertNotEqual(initial_state, changed_course.is_included)

    def test_get_by_id_nonexistent(self):
        self.app.logger.info('Запуск тестирования получения несуществующего курса по ID')
        with self.assertRaises(ValueError):
            course_service.get_by_id(999)

    def test_get_by_name_nonexistent(self):
        self.app.logger.info('Запуск тестирования получения несуществующего курса по имени')
        with self.assertRaises(ValueError):
            course_service.get_by_name('Non_Existent_Course')

    def test_create_without_course_type(self):
        self.app.logger.info('Запуск тестирования создания курса без типа')
        with self.assertRaises(ValueError):
            courseDTO = CourseDTO(name='Invalid Course')
            course_service.create(courseDTO)

    def test_get_all_empty(self):
        self.app.logger.info('Запуск тестирования получения курсов из пустой БД')
        self.assertEqual(len(course_service.get_all()), 0)

    def test_get_all_filtered(self):
        self.app.logger.info('Запуск тестирования фильтрации курсов')
        self.create_courses()
        course_type_service.create(CourseTypeDTO(name='Math'))
        another_type = course_type_service.get_by_name('Math')
        course_service.create(CourseDTO(name='Calculus', course_type_id=another_type.id))
        
        filtered = course_service.get_all(course_type=self.course_type.id)
        self.assertEqual(len(filtered), 3)
        
        included = course_service.get_all()
        self.assertEqual(len(included), 4)  

        included = course_service.get_all(included=True)
        self.assertEqual(len(included), 0)  



if __name__ == '__main__':
    unittest.main(verbosity=2)
