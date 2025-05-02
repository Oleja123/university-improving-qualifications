import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db

class Faculty(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(
        sa.String(128), index=True, unique=True)
    departments: so.WriteOnlyMapped['Department'] = so.relationship(
        back_populates='faculty', passive_deletes=True)

    def __repr__(self):
        return f'Faculty {self.name}'

    @classmethod
    def from_form(cls, form):
        return cls(name=form.name.data)