from datetime import date

import sqlalchemy as sa

from app.models.course import Course
from app.services import user_service
from app import db
from app.services.reports.pdf_draw_row import PdfDrawRow


class DirectionCreator(PdfDrawRow):

    def __init__(self, teacher, courses, date_from, date_to, admin):
        super().__init__()
        self.teacher = teacher
        self.courses = db.session.scalars(sa.select(Course).where(Course.id.in_(courses))).all()
        self.period = f"С {date_from} по {date_to}"
        self.admin = admin

    def create_latest_course_info(self, latest_course):
        return f"Тип курса: {latest_course.course.course_type.name}\n" +\
            f"Название курса: {latest_course.course.name}\n" +\
            f"Дата прохождения курса: {latest_course.date_completion.isoformat()}\n" +\
            f"№ подтверждающего документа: {latest_course.confirming_document}\n"

    def create_courses_info(self):
        res = ""
        for course in self.courses:
            res += f"{course.course_type.name}: {course.name}\n"
        return res

    def create_table(self):
        self.add_page()
        self.set_font("DejaVu", size=16)
        self.set_font(style="B")

        self.multi_cell(
            text=f"Справка представление", w=120, border=0, align='C')
        self.ln()

        self.set_font("DejaVu", size=10)
        self.set_font(style="B")
        self.draw_row(['Информация о слушателе'], [180])
        self.set_font(style="")
        self.draw_row(['ФИО', self.teacher.full_name], [90, 90])
        latest_course = user_service.get_latest_course(self.teacher.id)
        if latest_course is None:
            self.draw_row(['Последнее повышение квалификации:', 'Не проходилось'],
                          [90, 90])
        else:
            self.draw_row(['Последнее повышение квалификации:', self.create_latest_course_info(latest_course)],
                          [90, 90])
        self.set_font(style="B")
        self.draw_row(['Информация о программе повышения квалификации'], [180])
        self.set_font(style="")
        self.draw_row(['Наименования программ', self.create_courses_info()], [90, 90])
        self.draw_row(['Период прохождения повышения квалификации:', self.period],
                      [90, 90])
        self.draw_row(['Подпись преподавателя', ''],
                      [90, 90])
        self.draw_row(['Подпись сотрудника', ''],
                      [90, 90])
        self.draw_row(['Дата', date.today().isoformat()], [90, 90])
        self.draw_row(['ФИО сотрудника', self.admin.full_name], [90, 90])
