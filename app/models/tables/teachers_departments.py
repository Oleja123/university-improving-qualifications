import sqlalchemy as sa
from app import db

teachers_departments = sa.Table('teachers_departments',
                    db.metadata,
                    sa.Column('teacher_id', sa.Integer, sa.ForeignKey(
                        'user.id'), primary_key=True),
                    sa.Column('department_id', sa.Integer, sa.ForeignKey('department.id'), primary_key=True),)

from app.models.department import Department