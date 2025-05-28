from datetime import datetime

import sqlalchemy as sa
import sqlalchemy.orm as so

from app import db


class Course(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(
        sa.String(128), index=True, unique=True)
    course_type_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey('course_type.id', ondelete='CASCADE'), index=True)
    course_type: so.Mapped['CourseType'] = so.relationship(
        back_populates='courses')
    is_included: so.Mapped[bool] = so.mapped_column(
        sa.Boolean, index=True, default=False)
    teachers_courses: so.WriteOnlyMapped['TeacherCourse'] = so.relationship(
        back_populates='course', passive_deletes=True)

    def __repr__(self):
        return f'Course {self.name}'

    @classmethod
    def from_form(cls, form, course_type):
        return cls(name=form.name.data, course_type=course_type)
    
    def to_dict(self):
        data = {
            'id': self.id, 
            'name': self.name, 
            'course_type_id': self.course_type_id,
            'is_included': self.is_included
        }
        return data
