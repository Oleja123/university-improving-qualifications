from datetime import datetime
from app import db
from app.models.notification import Notification
from app.dto.notification_dto import NotificationDTO
from app.services import user_service
import sqlalchemy as sa


def get_by_id(id: int) :
    return db.session.get(Notification, id)

def send_message(notificaionDTO: NotificationDTO):
    user = user_service.get_by_id(notificaionDTO.user_id)
    notification = Notification(message=notificaionDTO.message, user=user, time_sent=datetime.now(), has_read=False)
    db.session.add(notification)
    db.session.commit()

def read_message(id):
    notification = get_by_id(id)
    notification.has_read = True
    db.session.commit()

