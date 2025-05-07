from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db
from app.models.tables.teachers_departments import teachers_departments
from flask_login import UserMixin


ADMIN = 0
TEACHER = 1
FIRED = 2


class User(UserMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(
        sa.String(64), index=True, unique=True)
    full_name: so.Mapped[str] = so.mapped_column(
        sa.String(128))
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    role: so.Mapped[bool] = so.mapped_column(sa.Boolean, index=True)
    notifications: so.WriteOnlyMapped['Notification'] = so.relationship(
        back_populates='user', passive_deletes=True)
    departments: so.WriteOnlyMapped['Department'] = so.relationship(
        secondary=teachers_departments, primaryjoin=(teachers_departments.c.teacher_id == id), back_populates='teachers', passive_deletes=True)
    courses: so.WriteOnlyMapped['TeacherCourse'] = so.relationship(
        back_populates='teacher', passive_deletes=True)

    def __repr__(self):
        return f'User {self.full_name}'

    @classmethod
    def from_form(cls, form, faculty):
        return cls(name=form.name.data, faculty=faculty)