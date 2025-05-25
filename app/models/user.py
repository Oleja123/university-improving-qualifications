from datetime import datetime
from typing import Optional

from flask import url_for
import sqlalchemy as sa
import sqlalchemy.orm as so
from flask_login import UserMixin

from app import db
from app.models.tables.teachers_departments import teachers_departments


ADMIN = 0
TEACHER = 1


class User(UserMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(
        sa.String(64), index=True, unique=True)
    full_name: so.Mapped[str] = so.mapped_column(
        sa.String(128))
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    role: so.Mapped[int] = so.mapped_column(sa.Integer, index=True)
    is_fired: so.Mapped[bool] = so.mapped_column(
        sa.Boolean, index=True, default=False)
    notifications: so.WriteOnlyMapped['Notification'] = so.relationship(
        back_populates='user', passive_deletes=True)
    departments: so.WriteOnlyMapped['Department'] = so.relationship(
        secondary=teachers_departments, primaryjoin=(teachers_departments.c.teacher_id == id), back_populates='teachers', passive_deletes=True)
    courses: so.WriteOnlyMapped['TeacherCourse'] = so.relationship(
        back_populates='teacher', passive_deletes=True)
    token: so.Mapped[Optional[str]] = so.mapped_column(
        sa.String(32), index=True, unique=True)
    token_expiration: so.Mapped[Optional[datetime]]

    def __repr__(self):
        return f'User {self.full_name}'

    def to_dict(self):
        data = {
            'id': self.id, 
            'username': self.username, 
            'full_name': self.full_name,
            'role': ('ADMIN' if self.role == 0 else 'TEACHER'),
            '_links': {
                'self': url_for('api.get_user', user_id=self.id),
                'notifications': url_for('api.get_user_notifications', user_id=self.id),
                'teacher_courses': url_for('api.get_teacher_courses', user_id=self.id),
                'revoke_token': url_for('api.revoke_user_token', user_id=self.id),
            }
        }
        return data