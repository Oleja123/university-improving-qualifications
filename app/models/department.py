import sqlalchemy as sa
import sqlalchemy.orm as so

from app import db
from app.models.tables.teachers_departments import teachers_departments


class Department(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(
        sa.String(128), index=True, unique=True)
    faculty_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey('faculty.id', ondelete='CASCADE'), index=True)
    faculty: so.Mapped['Faculty'] = so.relationship(
        back_populates='departments')
    teachers: so.WriteOnlyMapped['User'] = so.relationship(
        secondary=teachers_departments, primaryjoin=(teachers_departments.c.department_id == id), back_populates='departments', passive_deletes=True)

    def __repr__(self):
        return f'Department {self.name}'

    @classmethod
    def from_form(cls, form, faculty):
        return cls(name=form.name.data, faculty=faculty)
