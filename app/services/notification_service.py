from app import db, app
from app.models.notification import Notification
from app.dto.notification_dto import NotificationDTO
from app.services import user_service
import sqlalchemy as sa


def get_by_id(id: int) :
    try:
        res = db.session.get(Notification, id)
        if res is None:
            raise ValueError(f'Уведомление с id = {id} не существует')
        return res
    except ValueError as e:
        db.session.rollback()
        app.logger.error(e)
        raise
    except Exception as e:
        db.session.rollback()
        app.logger.error(e)
        raise Exception('Неизвестная ошибка')

def send_message(notificationDTO: NotificationDTO):
    try:
        user = user_service.get_by_id(notificationDTO.user_id)
        notification = Notification(message=notificationDTO.message, user=user, has_read=False)
        db.session.add(notification)
        db.session.commit()
    except ValueError:
        db.session.rollback()
        raise
    except Exception as e:
        db.session.rollback()
        app.logger.error(e)
        raise Exception('Неизвестная ошибка')


def read_message(id):
    try:
        notification = get_by_id(id)
        notification.has_read = True
        db.session.commit()
    except ValueError:
        db.session.rollback()
        raise
    except Exception as e:
        db.session.rollback()
        app.logger.error(e)
        raise Exception('Неизвестная ошибка')
    
def get_user_notifications_count(user_id):
    try:
        query = sa.select(sa.func.count()).where(sa.and_(Notification.has_read == False, Notification.user_id == user_id))
        return db.session.scalar(query)
    except Exception as e:
        db.session.rollback()
        app.logger.error(e)
        raise Exception('Неизвестная ошибка')
    
def delete(id):
    try:
        message = get_by_id(id)
        db.session.delete(message)
        db.session.commit()
    except ValueError:
        db.session.rollback()
        raise
    except Exception as e:
        db.session.rollback()
        app.logger.error(e)
        raise Exception('Неизвестная ошибка')

