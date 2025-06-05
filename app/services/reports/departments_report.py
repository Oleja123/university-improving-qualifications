from flask import current_app
import sqlalchemy as sa

from app.models.department import Department
from app.models.faculty import Faculty
from app.models.teacher_course import TeacherCourse
from app.models.user import User
from app.services import faculty_service
from app import db


class DepartmentsReport:

    def __init__(self, faculty_id, date_from, date_to):
        self.faculty = faculty_service.get_by_id(faculty_id)
        self.date_from = f"От: {date_from}"
        self.date_to = f"До: {date_to}"
        self.table_header = ['Название кафедры', 'Количество пройденных курсов', '% относительно всех пройденных курсов факультета за период']
        self.filter_item_name = self.faculty.name
        current_app.logger.info(f"Дата начала: {date_from}")
        current_app.logger.info(f"Дата конца: {date_to}")
        subquery1 = sa.select(TeacherCourse.teacher_id, TeacherCourse.course_id)\
                      .join(User)\
                      .join(User.departments)\
                      .where(
                          sa.and_(
                              Department.faculty_id == faculty_id,
                              TeacherCourse.date_completion >= date_from,
                              TeacherCourse.date_completion <= date_to
                          )     
                        )\
                      .distinct()\
                      .subquery()
        query = sa.select(sa.func.count().label('faculty_total'))\
                     .select_from(subquery1)
        
        cnt = db.session.scalar(query)
        current_app.logger.info(f"Количество: {cnt}")
        count_expr = sa.func.count().label('on_department')

        query = sa.select(Department.name, 
                          count_expr,
                          sa.func.round(count_expr * 100.0 / cnt, 2).label('on_department_percent')
                          ).select_from(Faculty)\
                          .join(Faculty.departments)\
                          .join(Department.teachers)\
                          .join(User.courses)\
                          .where(sa.and_(TeacherCourse.date_completion >= date_from, 
                                         TeacherCourse.date_completion <= date_to,
                                         Department.faculty_id == faculty_id,
                                         ))\
                          .group_by(Department.id, Department.name)\
                          .order_by(Department.name)
        self.result = cnt
        self.percent_target = 'Проценты'
        self.percent = f"{100}%"
        self.rows = db.session.execute(query).all()
        self.rows = list(map(lambda x: [x[0], x[1], f"{x[2]}%"], self.rows))
        current_app.logger.info(f"Результат: {self.rows}")