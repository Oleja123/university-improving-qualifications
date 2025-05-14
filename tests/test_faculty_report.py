import os

from app.dto.course_dto import CourseDTO
from app.dto.course_type_dto import CourseTypeDTO
from app.dto.department_dto import DepartmentDTO
from app.dto.faculty_dto import FacultyDTO
from app.dto.user_dto import UserDTO
os.environ['DATABASE_URL'] = 'sqlite://'

from datetime import datetime, timedelta
from app.models import Course, Department, Faculty, TeacherCourse, User, user
from app.services import course_service, course_type_service, department_service, faculty_service, user_service
from app import app, db
import unittest

class FacultyReportTestCase(unittest.TestCase):
    def setUp(self):
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()
        
        faculty_service.create(FacultyDTO(name='test faculty'))
        self.faculty = faculty_service.get_by_name('test faculty')
        
        department_service.create(DepartmentDTO(name='test department', faculty_id=self.faculty.id))
        self.department = department_service.get_by_name('test department')
        
        user_service.create(UserDTO(full_name='tester', username='tester', password='test_password', role=user.TEACHER))
        self.teacher = user_service.get_by_username('tester')
        
        course_type_service.create(CourseTypeDTO(name='test course type'))
        self.course_type = course_type_service.get_by_name('test course type')

        course_service.create(CourseDTO(name='test course', course_type_id=self.course_type.id))
        self.course1 = course_service.get_by_name('test course')
        
        course_service.create(CourseDTO(name='test course', course_type_id=self.course_type.id))
        self.course1 = course_service.get_by_name('test course')

        user_service.add_to_department(self.teacher.id, self.department.id)
        
        sertificate_service
        # Добавляем подтвержденный курс
        self.approved_course = TeacherCourse(
            teacher=self.teacher,
            course=self.course,
            date_approved=datetime.now()
        )
        db.session.add(self.approved_course)
        
        # Добавляем неподтвержденный курс (не должен попасть в отчет)
        self.unapproved_course = TeacherCourse(
            teacher=self.teacher,
            course=self.course,
            date_approved=None
        )
        db.session.add(self.unapproved_course)
        
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_report_initialization(self):
        """Тест инициализации отчета"""
        report = FacultyReport(self.faculty.id)
        
        self.assertEqual(report.faculty.id, self.faculty.id)
        self.assertEqual(report.faculty_name, self.faculty.name)
        self.assertEqual(len(report.table_header), 4)
        self.assertGreater(report.result, 0)

    def test_report_content(self):
        """Тест содержимого отчета"""
        report = FacultyReport(self.faculty.id)
        
        # Проверяем, что есть хотя бы одна строка
        self.assertGreater(len(report.rows), 0)
        
        # Проверяем структуру данных
        first_row = report.rows[0]
        self.assertEqual(len(first_row), 4)
        self.assertEqual(first_row[0], self.teacher.full_name)
        self.assertEqual(first_row[1], self.teacher.username)
        self.assertEqual(first_row[2], self.course.name)
        self.assertIsInstance(first_row[3], datetime)

    def test_report_excludes_unapproved_courses(self):
        """Тест, что неподтвержденные курсы не попадают в отчет"""
        # Добавляем еще один неподтвержденный курс
        new_course = Course(name="Неподтвержденный курс", is_included=True)
        db.session.add(new_course)
        db.session.commit()
        
        TeacherCourse(
            teacher=self.teacher,
            course=new_course,
            date_approved=None
        )
        db.session.commit()
        
        report = FacultyReport(self.faculty.id)
        courses_in_report = [row[2] for row in report.rows]
        self.assertNotIn("Неподтвержденный курс", courses_in_report)

    def test_report_excludes_fired_teachers(self):
        """Тест, что уволенные преподаватели не попадают в отчет"""
        # Создаем уволенного преподавателя
        fired_teacher = User(
            username="fired_teacher",
            full_name="Петров Петр",
            role=1,  # TEACHER
            is_fired=True
        )
        db.session.add(fired_teacher)
        fired_teacher.departments.append(self.department)
        
        # Добавляем подтвержденный курс уволенному преподавателю
        TeacherCourse(
            teacher=fired_teacher,
            course=self.course,
            date_approved=datetime.now()
        )
        db.session.commit()
        
        report = FacultyReport(self.faculty.id)
        teachers_in_report = [row[0] for row in report.rows]
        self.assertNotIn("Петров Петр", teachers_in_report)

    def test_report_ordering(self):
        """Тест сортировки по дате подтверждения"""
        # Добавляем курс с более поздней датой
        new_course = Course(name="Новый курс", is_included=True)
        db.session.add(new_course)
        
        future_date = datetime.now() + timedelta(days=1)
        TeacherCourse(
            teacher=self.teacher,
            course=new_course,
            date_approved=future_date
        )
        db.session.commit()
        
        report = FacultyReport(self.faculty.id)
        
        # Проверяем, что первым идет курс с более поздней датой
        self.assertEqual(report.rows[0][2], "Новый курс")
        self.assertEqual(report.rows[1][2], "Тестовый курс")

    def test_report_for_nonexistent_faculty(self):
        """Тест обработки несуществующего факультета"""
        with self.assertRaises(AttributeError):
            report = FacultyReport(999)  # Несуществующий ID
            _ = report.rows  # Попытка доступа к данным

    def test_report_with_no_data(self):
        """Тест отчета для факультета без данных"""
        # Создаем пустой факультет
        empty_faculty = Faculty(name="Пустой факультет")
        db.session.add(empty_faculty)
        db.session.commit()
        
        report = FacultyReport(empty_faculty.id)
        
        self.assertEqual(report.result, 0)
        self.assertEqual(len(report.rows), 0)

    def test_report_distinct_entries(self):
        """Тест на уникальность записей в отчете"""
        # Добавляем дублирующую запись (преподаватель + курс)
        TeacherCourse(
            teacher=self.teacher,
            course=self.course,
            date_approved=datetime.now()
        )
        db.session.commit()
        
        report = FacultyReport(self.faculty.id)
        
        # Проверяем, что в отчете только уникальные записи
        courses_count = sum(1 for row in report.rows if row[2] == "Тестовый курс")
        self.assertEqual(courses_count, 1)

if __name__ == '__main__':
    unittest.main(verbosity=2)