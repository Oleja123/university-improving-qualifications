import os
import unittest

from tests.test_config import TestConfig
from app.dto.department_dto import DepartmentDTO
from app.dto.faculty_dto import FacultyDTO
from app.services import department_service, faculty_service
from app import create_app, db


os.environ['DATABASE_URL'] = 'sqlite://'


class DepartmentServiceCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        faculty_service.create(FacultyDTO(name='Test Faculty'))
        self.faculty = faculty_service.get_by_id(1)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def create_departments(self):
        test_departments = [
            DepartmentDTO(name='IS', faculty_id=self.faculty.id),
            DepartmentDTO(name='CT', faculty_id=self.faculty.id),
            DepartmentDTO(name='AB', faculty_id=self.faculty.id),
        ]
        for department in test_departments:
            department_service.create(department)

    def test_create(self):
        self.app.logger.info('Запуск теста создания кафедры')
        departmentDTO = DepartmentDTO(
            name='Test Department', faculty_id=self.faculty.id)
        department_service.create(departmentDTO)
        created = department_service.get_by_name(departmentDTO.name)
        self.assertEqual(created.name, 'Test Department')
        self.assertEqual(created.faculty_id, self.faculty.id)

    def test_update(self):
        self.app.logger.info('Запуск тестирования обновления кафедры')
        faculty_service.create(FacultyDTO(name='FIST'))
        new_faculty = faculty_service.get_by_name('FIST')
        new_name = 'SF'
        department_service.create(DepartmentDTO(
            name='test', faculty_id=self.faculty.id))
        department = department_service.get_by_name('test')
        departmentDTO = DepartmentDTO(
            id=department.id, name=new_name, faculty_id=new_faculty.id)
        department_service.update(departmentDTO)
        department = department_service.get_by_id(department.id)
        self.assertTrue(department is not None and department.name ==
                        new_name and department.faculty.id == new_faculty.id)

    def test_delete(self):
        self.app.logger.info('Запуск тестирования удаления кафедры')
        department_service.create(DepartmentDTO(
            name='test', faculty_id=self.faculty.id))
        department = department_service.get_by_name('test')
        department_service.delete(department.id)
        with self.assertRaises(ValueError):
            department = department_service.get_by_id(department.id)

    def test_department_faculty_relationship(self):
        self.app.logger.info('Запуск теста связи кафедры с факультетом')
        department_service.create(DepartmentDTO(
            name='CS', faculty_id=self.faculty.id))
        department = department_service.get_by_name('CS')
        self.assertEqual(department.faculty.name, 'Test Faculty')
        self.assertIn(department, faculty_service.get_departments(
            FacultyDTO(department.faculty.id)))

    def test_cascade_on_faculty_delete(self):
        self.app.logger.info(
            'Запуск теста каскадного удаления при удалении факультета')
        department_service.create(DepartmentDTO(
            name='Math', faculty_id=self.faculty.id))
        faculty_service.delete(self.faculty.id)
        with self.assertRaises(ValueError):
            deleted = department_service.get_by_name('Math')

    def test_same_name_create(self):
        self.app.logger.info('Запуск теста уникальности имени кафедры')
        department_service.create(DepartmentDTO(
            name='Chemistry', faculty_id=self.faculty.id))
        with self.assertRaises(ValueError):
            department_service.create(DepartmentDTO(
                name='Chemistry', faculty_id=self.faculty.id))

    def test_get_by_id_nonexistent(self):
        self.app.logger.info(
            'Запуск теста получения несуществующей кафедры по ID')
        with self.assertRaises(ValueError):
            department = department_service.get_by_id(999)

    def test_get_by_name_nonexistent(self):
        self.app.logger.info(
            'Запуск теста получения несуществующей кафедры по имени')
        with self.assertRaises(ValueError):
            department = department_service.get_by_name('NON_EXISTENT')

    def test_get_all(self):
        self.app.logger.info('Запуск получения всех кафедр')
        self.create_departments()
        self.assertTrue(len(department_service.get_all()) == 3)

    def test_get_all_empty(self):
        self.app.logger.info('Запуск теста получения всех кафедр из пустой БД')
        self.assertEqual(len(department_service.get_all()), 0)

    def test_get_all_paginated(self):
        self.app.logger.info('Запуск теста пагинации кафедр')
        self.create_departments()

        page1 = department_service.get_all_paginated(page=1)
        self.assertEqual(len(page1.items), 3)
        self.assertEqual(page1.page, 1)
        self.assertEqual(
            page1.per_page, self.app.config['DEPARTMENTS_PER_PAGE'])
        self.assertFalse(page1.has_prev)
        self.assertFalse(page1.has_next)

        original_per_page = self.app.config['DEPARTMENTS_PER_PAGE']
        self.app.config['DEPARTMENTS_PER_PAGE'] = 2

        page1 = department_service.get_all_paginated(page=1)
        self.assertEqual(len(page1.items), 2)
        self.assertTrue(page1.has_next)
        self.assertFalse(page1.has_prev)

        page2 = department_service.get_all_paginated(page=2)
        self.app.logger.info(page2.items)
        self.assertEqual(len(page2.items), 1)
        self.assertFalse(page2.has_next)
        self.assertTrue(page2.has_prev)
        self.app.config['DEPARTMENTS_PER_PAGE'] = original_per_page

    def test_get_all_paginated_empty(self):
        self.app.logger.info('Запуск теста пагинации с пустым списком кафедр')
        page = department_service.get_all_paginated(page=1)
        self.assertEqual(len(page.items), 0)
        self.assertEqual(page.total, 0)
        self.assertFalse(page.has_prev)
        self.assertFalse(page.has_next)

    def test_get_all_paginated_empty(self):
        self.app.logger.info('Запуск теста пагинации с пустым списком кафедр')
        page = department_service.get_all_paginated(page=1)
        self.assertEqual(len(page.items), 0)
        self.assertEqual(page.total, 0)
        self.assertFalse(page.has_prev)
        self.assertFalse(page.has_next)

    def test_get_all_paginated_with_faculty_filter(self):
        self.app.logger.info('Запуск теста пагинации с фильтром по факультету')
        faculty_service.create(FacultyDTO(name='Another Faculty'))
        faculty2 = faculty_service.get_by_name('Another Faculty')

        department_service.create(DepartmentDTO(
            name='Dep1', faculty_id=faculty2.id))
        department_service.create(DepartmentDTO(
            name='Dep2', faculty_id=faculty2.id))

        original_per_page = self.app.config['DEPARTMENTS_PER_PAGE']
        self.app.config['DEPARTMENTS_PER_PAGE'] = 1

        page1 = department_service.get_all_paginated(
            page=1, faculties=[faculty2.id])
        self.assertEqual(len(page1.items), 1)
        self.assertEqual(page1.items[0].name, 'Dep1')
        self.assertTrue(page1.has_next)

        page2 = department_service.get_all_paginated(
            page=2, faculties=[faculty2.id])
        self.assertEqual(len(page2.items), 1)
        self.assertEqual(page2.items[0].name, 'Dep2')
        self.assertFalse(page2.has_next)
        self.app.config['DEPARTMENTS_PER_PAGE'] = original_per_page


if __name__ == '__main__':
    unittest.main(verbosity=2)
