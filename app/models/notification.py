import sqlalchemy as sa
import sqlalchemy.orm as so
from datetime import datetime, timezone
from app import db


class Notification(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    message: so.Mapped[str] = so.mapped_column(
        sa.String(256), index=True, unique=True)
    user_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey('user.id', ondelete='CASCADE'), index=True)
    user: so.Mapped['User'] = so.relationship(
        back_populates='notifications')
    has_read: so.Mapped[bool] = so.mapped_column(sa.Boolean)
    time_sent: so.Mapped[datetime] = so.mapped_column(index=True, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f'Notification {self.message}'

    @classmethod
    def from_form(cls, form, faculty):
        return cls(name=form.name.data, faculty=faculty)