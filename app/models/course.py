import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db
from datetime import datetime


class Course(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(
        sa.String(128), index=True, unique=True)
    course_type_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey('course_type.id', ondelete='CASCADE'), index=True)
    course_type: so.Mapped['CourseType'] = so.relationship(
        back_populates='courses')
    is_included: so.Mapped[bool] = so.mapped_column(sa.Boolean, index=True, default=False)

    def __repr__(self):
        return f'Course {self.name}'

    @classmethod
    def from_form(cls, form, type):
        return cls(name=form.name.data, type=type)