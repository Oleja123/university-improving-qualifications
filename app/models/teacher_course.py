from datetime import datetime
from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db


class TeacherCourse(db.Model):
    teacher_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey('user.id'), primary_key=True, index=True)
    teacher: so.Mapped['User'] = so.relationship(
        back_populates='courses')
    course_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey('course.id'), primary_key=True, index=True)
    course = db.relationship('Course')
    sertificate_path: so.Mapped[Optional[str]] = so.mapped_column(
        sa.String(260), unique=True)
    date_approved: so.Mapped[Optional[datetime]] = so.mapped_column(sa.DateTime)

    def __repr__(self):
        return f'Teacher Course {self.teacher.name}, {self.course.name}'

    @classmethod
    def from_form(cls, form, faculty):
        return cls(name=form.name.data, faculty=faculty)