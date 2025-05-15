from typing import Optional
from datetime import datetime, timezone

import sqlalchemy as sa
import sqlalchemy.orm as so

from app import db


def add_years(start_date, years):
    try:
        return start_date.replace(year=start_date.year + years)
    except ValueError:
        return start_date.replace(year=start_date.year + years, day=28)


class CourseType(db.Model):
    __tablename__ = 'course_type'
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(
        sa.String(128), index=True, unique=True)
    courses: so.WriteOnlyMapped['Course'] = so.relationship(
        back_populates='course_type', passive_deletes=True)
    deadline: so.Mapped[Optional[datetime]] = so.mapped_column(
        index=True, default=lambda: add_years(datetime.now(timezone.utc), 3))

    def __repr__(self):
        return f'Course Type {self.name}'

    @classmethod
    def from_form(cls, form, faculty):
        return cls(name=form.name.data, faculty=faculty)
