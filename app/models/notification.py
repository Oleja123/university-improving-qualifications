from datetime import datetime, timezone

from flask import url_for
import sqlalchemy as sa
import sqlalchemy.orm as so

from app import db


class Notification(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    message: so.Mapped[str] = so.mapped_column(
        sa.String(256), index=True)
    user_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey('user.id', ondelete='CASCADE'), index=True)
    user: so.Mapped['User'] = so.relationship(
        back_populates='notifications')
    has_read: so.Mapped[bool] = so.mapped_column(sa.Boolean, default=False)
    time_sent: so.Mapped[datetime] = so.mapped_column(
        index=True, default=lambda: datetime.now())

    def __repr__(self):
        return f'Notification {self.message}'

    @classmethod
    def from_form(cls, form, user):
        return cls(name=form.message.data, user=user)

    def to_dict(self):
        data = {
            'id': self.id, 
            'message': self.message, 
            'user_id': self.user_id,
            'has_read': self.has_read,
            'time_sent': self.time_sent.isoformat(),
            '_links': {
                'self': url_for('api.get_notification', id=self.id),
            }
        }
        return data