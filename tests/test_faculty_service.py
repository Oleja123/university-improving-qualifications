import os

from tests.test_config import TestConfig
os.environ['DATABASE_URL'] = 'sqlite://'

from app.dto.faculty_dto import FacultyDTO
from app.services import faculty_service
from app import create_app, db
import unittest


class FacultyServiceCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def create_faculties(self):
        test_faculties = [
            FacultyDTO(name='FIST'),
            FacultyDTO(name='EF'),
            FacultyDTO(name='RTF')
        ]
        for faculty in test_faculties:
            faculty_service.create(faculty)

    def test_create(self):
        self.app.logger.info('Запуск тестирования создания факультета')
        facultyDTO = FacultyDTO(name='GF')
        faculty_service.create(facultyDTO)
        created_faculty = faculty_service.get_by_name(facultyDTO.name)
        self.assertTrue(
            created_faculty is not None and facultyDTO.name == created_faculty.name)

    def test_update(self):
        self.app.logger.info('Запуск тестирования обновления факультетов')
        self.create_faculties()
        faculty = faculty_service.get_by_name('EF')
        new_name = 'SF'
        facultyDTO = FacultyDTO(id=faculty.id, name=new_name)
        faculty_service.update(facultyDTO)
        faculty = faculty_service.get_by_id(faculty.id)
        self.assertTrue(faculty is not None and faculty.name == new_name)

    def test_delete(self):
        self.app.logger.info('Запуск тестирования удаления факультета')
        self.create_faculties()
        faculty = faculty_service.get_by_id(1)
        faculty_service.delete(faculty.id)
        with self.assertRaises(ValueError):
            faculty = faculty_service.get_by_id(faculty.id)

    def test_get_all(self):
        self.app.logger.info('Запуск получения всех факультетов')
        self.create_faculties()
        self.assertTrue(len(faculty_service.get_all()) == 3)

    def test_same_name_create(self):
        self.app.logger.info('Запуск проверки на одинаковые имена')
        self.create_faculties()
        with self.assertRaises(ValueError):
            facultyDTO = FacultyDTO(name='FIST')
            faculty_service.create(facultyDTO)

    def test_get_by_id_nonexistent(self):
        self.app.logger.info('Запуск теста получения несуществующего факультета по ID')
        with self.assertRaises(ValueError):
            faculty = faculty_service.get_by_id(999)

    def test_get_by_name_nonexistent(self):
        self.app.logger.info('Запуск теста получения несуществующего факультета по имени')
        with self.assertRaises(ValueError):
            faculty = faculty_service.get_by_name('NON_EXISTENT')

    def test_get_all_empty(self):
        self.app.logger.info('Запуск теста получения всех факультетов из пустой БД')
        self.assertEqual(len(faculty_service.get_all()), 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)
