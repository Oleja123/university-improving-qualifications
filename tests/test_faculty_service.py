from sqlite3 import DataError
from app.dto.faculty_dto import FacultyDTO
from sqlalchemy.exc import IntegrityError
from app.services import faculty_service
from app.models.faculty import Faculty
from app import app, db, logging
import unittest
import os
os.environ['DATABASE_URL'] = 'sqlite://'


class FacultyServiceCase(unittest.TestCase):
    def setUp(self):
        self.app_context = app.app_context()
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
        app.logger.info('Запуск тестирования создания факультета')
        facultyDTO = FacultyDTO(name='GF')
        faculty_service.create(facultyDTO)
        created_faculty = faculty_service.get_by_name(facultyDTO.name)
        self.assertTrue(
            created_faculty is not None and facultyDTO.name == created_faculty.name)

    def test_update(self):
        app.logger.info('Запуск тестирования обновления факультетов')
        self.create_faculties()
        faculty = faculty_service.get_by_name('EF')
        new_name = 'SF'
        facultyDTO = FacultyDTO(id=faculty.id, name=new_name)
        faculty_service.update(facultyDTO)
        faculty = faculty_service.get_by_id(faculty.id)
        self.assertTrue(faculty is not None and faculty.name == new_name)

    def test_delete(self):
        app.logger.info('Запуск тестирования удаления факультета')
        self.create_faculties()
        faculty = faculty_service.get_by_id(1)
        faculty_service.delete(faculty.id)
        faculty = faculty_service.get_by_id(faculty.id)
        self.assertTrue(faculty is None)

    def test_get_all(self):
        app.logger.info('Запуск получения всех факультетов')
        self.create_faculties()
        self.assertTrue(len(faculty_service.get_all()) == 3)

    def test_same_name_create(self):
        app.logger.info('Запуск проверки на одинаковые имена')
        self.create_faculties()
        with self.assertRaises(IntegrityError):
            facultyDTO = FacultyDTO(name='FIST')
            faculty_service.create(facultyDTO)

    def test_get_by_id_nonexistent(self):
        app.logger.info('Запуск теста получения несуществующего факультета по ID')
        faculty = faculty_service.get_by_id(999)
        self.assertIsNone(faculty)

    def test_get_by_name_nonexistent(self):
        app.logger.info('Запуск теста получения несуществующего факультета по имени')
        faculty = faculty_service.get_by_name('NON_EXISTENT')
        self.assertIsNone(faculty)

    def test_get_all_empty(self):
        app.logger.info('Запуск теста получения всех факультетов из пустой БД')
        self.assertEqual(len(faculty_service.get_all()), 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)
