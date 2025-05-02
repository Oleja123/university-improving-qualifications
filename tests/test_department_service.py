from app.dto.department_dto import DepartmentDTO
from app.dto.faculty_dto import FacultyDTO
from sqlalchemy.exc import IntegrityError
from app.services import department_service, faculty_service
from app.models.faculty import Faculty
from app.models.department import Department
from app import app, db
import unittest
import os
os.environ['DATABASE_URL'] = 'sqlite://'


class DepartmentServiceCase(unittest.TestCase):
    def setUp(self):
        self.app_context = app.app_context()
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
            DepartmentDTO(name='AB', faculty_id=self.faculty.id)
        ]
        for department in test_departments:
            department_service.create(department)

    def test_create(self):
        app.logger.info('Запуск теста создания кафедры')
        departmentDTO = DepartmentDTO(name='Test Department', faculty_id=self.faculty.id)
        department_service.create(departmentDTO)
        created = department_service.get_by_name(departmentDTO.name)
        self.assertEqual(created.name, 'Test Department')
        self.assertEqual(created.faculty_id, self.faculty.id)

    def test_update(self):
        app.logger.info('Запуск тестирования обновления кафедры')
        faculty_service.create(FacultyDTO(name='FIST'))
        new_faculty = faculty_service.get_by_name('FIST')
        new_name = 'SF'
        department_service.create(DepartmentDTO(name='test', faculty_id=self.faculty.id))
        department = department_service.get_by_name('test')
        departmentDTO = DepartmentDTO(id=department.id, name=new_name, faculty_id=new_faculty.id)
        department_service.update(departmentDTO)
        department = department_service.get_by_id(department.id)
        self.assertTrue(department is not None and department.name == new_name and department.faculty.id == new_faculty.id)

    def test_delete(self):
        app.logger.info('Запуск тестирования удаления кафедры')
        department_service.create(DepartmentDTO(name='test', faculty_id=self.faculty.id))
        department = department_service.get_by_name('test')
        department_service.delete(department.id)
        department = department_service.get_by_id(department.id)
        self.assertTrue(department is None)

    def test_department_faculty_relationship(self):
        app.logger.info('Запуск теста связи кафедры с факультетом')
        department_service.create(DepartmentDTO(name='CS', faculty_id=self.faculty.id))
        department = department_service.get_by_name('CS')
        self.assertEqual(department.faculty.name, 'Test Faculty')
        self.assertIn(department, faculty_service.get_departments(FacultyDTO(department.faculty.id)))

    # def test_cascade_on_faculty_delete(self): #когда постгру поставлю проверю
    #     app.logger.info('Запуск теста каскадного удаления при удалении факультета')
    #     department_service.create(DepartmentDTO(name='Math', faculty_id=self.faculty.id))
    #     faculty_service.delete(self.faculty.id)
    #     deleted = department_service.get_by_name('Math')
    #     self.assertIsNone(deleted)

    def test_same_name_create(self):
        app.logger.info('Запуск теста уникальности имени кафедры')
        department_service.create(DepartmentDTO(name='Chemistry', faculty_id=self.faculty.id))
        with self.assertRaises(IntegrityError):
            department_service.create(DepartmentDTO(name='Chemistry', faculty_id=self.faculty.id))

    def test_get_all(self):
        app.logger.info('Запуск получения всех кафедр')
        self.create_departments()
        self.assertTrue(len(department_service.get_all()) == 3)

    def test_get_all_empty(self):
        app.logger.info('Запуск теста получения всех кафедр из пустой БД')
        self.assertEqual(len(department_service.get_all()), 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)
