from datetime import datetime
from typing import Optional

import sqlalchemy as sa
import sqlalchemy.orm as so

from app import db


class TeacherCourse(db.Model):
    teacher_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey('user.id', ondelete='CASCADE'), primary_key=True, index=True)
    teacher: so.Mapped['User'] = so.relationship(
        back_populates='courses')
    course_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey('course.id', ondelete='CASCADE'), primary_key=True, index=True)
    course: so.Mapped['Course'] = so.relationship(
        back_populates='teachers_courses')
    sertificate_path: so.Mapped[Optional[str]] = so.mapped_column(
        sa.String(260), unique=True, nullable=True)
    date_approved: so.Mapped[Optional[datetime]
                             ] = so.mapped_column(sa.DateTime, nullable=True)

    def __repr__(self):
        return f'Teacher Course {self.teacher.full_name}, {self.course.name}'
