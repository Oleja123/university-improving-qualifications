from flask import current_app
import sqlalchemy as sa

from app import db
from app.models.notification import Notification
from app.dto.notification_dto import NotificationDTO
from app.services import user_service


def notifications_key(user_id):
    return f"notifications:{user_id}"


def get_by_id(id: int):
    try:
        res = db.session.get(Notification, id)
        if res is None:
            raise ValueError(f'Уведомление с id = {id} не существует')
        return res
    except ValueError as e:
        current_app.logger.error(e)
        raise
    except Exception as e:
        current_app.logger.error(e)
        raise Exception('Ошибка при получении уведомления по id')


def send_message(notificationDTO: NotificationDTO):
    try:
        user = user_service.get_by_id(notificationDTO.user_id)
        notification = Notification(
            message=notificationDTO.message, user=user, has_read=False)
        db.session.add(notification)
        db.session.commit()
        r = current_app.config['SESSION_REDIS']
        r.delete(notifications_key(user.id))
    except ValueError as e:
        current_app.logger.error(e)
        raise
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        raise Exception('Ошибка при отправке сообщения')


def read_message(id):
    try:
        notification = get_by_id(id)
        notification.has_read = True
        db.session.commit()
        r = current_app.config['SESSION_REDIS']
        r.delete(notifications_key(notification.user_id))
    except ValueError as e:
        current_app.logger.error(e)
        raise
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        raise Exception('Ошибка при прочтении сообщения')


def get_user_notifications_count(user_id):
    try:
        r = current_app.config['SESSION_REDIS']
        cur_key = notifications_key(user_id)
        if r.exists(cur_key):
            return int(r.get(cur_key))
        query = sa.select(sa.func.count()).where(
            sa.and_(Notification.has_read == False, Notification.user_id == user_id))
        res = db.session.scalar(query)
        r.setex(cur_key, 86400, res)
        return res
    except Exception as e:
        current_app.logger.error(e)
        raise Exception('Ошибка при получении количества сообщений')


def delete(id):
    try:
        notification = get_by_id(id)
        db.session.delete(notification)
        db.session.commit()
        r = current_app.config['SESSION_REDIS']
        r.delete(notifications_key(notification.user_id))
    except ValueError as e:
        current_app.logger.error(e)
        raise
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        raise Exception('Ошибка при удалении сообщения')
