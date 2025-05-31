from datetime import datetime
from typing import Optional

from flask import url_for
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
    date_completion: so.Mapped[Optional[datetime]
                             ] = so.mapped_column(sa.Date, nullable=True)

    def __repr__(self):
        return f'Teacher Course {self.teacher.full_name}, {self.course.name}'
    
    def to_dict(self):
        data = {
            'teacher_id': self.teacher_id, 
            'course_id': self.course_id, 
            'date_completion': (self.date_completion.isoformat() if self.date_completion else None),
            'course_name': self.course.name,
            'sertificate_loaded': (self.sertificate_path is not None),
            '_links': {
                'self': url_for('api.get_teacher_course', user_id=self.teacher_id, course_id=self.course_id),
            }
        }
        return data
