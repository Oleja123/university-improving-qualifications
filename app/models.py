from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login
from flask_login import UserMixin

user_role = sa.Table(
    'users_roles',
    db.metadata,
    sa.Column('teacher_id', sa.Integer, sa.ForeignKey('user.id', ondelete='CASCADE'),
              primary_key=True, unique=True),
    sa.Column('role_id', sa.Integer, sa.ForeignKey('role.id', ondelete='CASCADE'),
              primary_key=True)
)


teachers_departments = sa.Table(
    'teachers_departments',
    db.metadata,
    sa.Column('teacher_id', sa.Integer, sa.ForeignKey(
        'user.id'), primary_key=True),
    sa.Column('department_id', sa.Integer, sa.ForeignKey(
        'department.id'), primary_key=True)
)


@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))


class User(UserMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(
        sa.String(64), index=True, unique=True)
    full_name: so.Mapped[str] = so.mapped_column(sa.String(64))
    email: so.Mapped[str] = so.mapped_column(
        sa.String(120), index=True, unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    role: so.Mapped['Role'] = so.relationship(secondary=user_role)
    departments: so.WriteOnlyMapped['Department'] = so.relationship(secondary=teachers_departments,
                                                                    primaryjoin=(
                                                                        teachers_departments.c.teacher_id == id),
                                                                    back_populates='teachers')

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def check_role(self, role: str) -> bool:
        if role is None:
            return False
        return self.role.name == role

    def set_role(self, role: str) -> bool:
        if self.role is not None:
            return False
        role = db.session.scalar(sa.select(Role).where(Role.name == role))
        if role is None:
            return False
        self.role = role
        return True

    def __repr__(self):
        return f'User {self.username}'


class Role(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(
        sa.String(64), index=True, unique=True)

    def __repr__(self):
        return f'Role {self.name}'


class Faculty(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(
        sa.String(128), index=True, unique=True)
    departments: so.WriteOnlyMapped['Department'] = so.relationship(
        back_populates='faculty', passive_deletes=True)

    def __repr__(self):
        return f'Faculty {self.name}'


class Department(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(
        sa.String(128), index=True, unique=True)
    faculty_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey(Faculty.id, ondelete='CASCADE'), index=True, nullable=True)
    faculty: so.Mapped[Faculty] = so.relationship(back_populates='departments')
    teachers: so.WriteOnlyMapped['User'] = so.relationship(secondary=teachers_departments,
                                                           primaryjoin=(
                                                               teachers_departments.c.department_id == id),
                                                           back_populates='departments', passive_deletes=True)
    
    def add_teacher(self, teacher: User) -> bool:
        if teacher.role.name != 'Teacher':
            return False
        self.teachers.add(teacher)
        return True

    def __repr__(self):
        return f'Department {self.name}'
