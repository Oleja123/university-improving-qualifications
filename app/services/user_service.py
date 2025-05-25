from datetime import datetime, timedelta
import secrets
from flask import current_app
import sqlalchemy as sa
from app.exceptions.fired_error import FiredError
from app.exceptions.wrong_password_error import WrongPasswordError

from app import db
from app.models.user import User
from app.models.teacher_course import TeacherCourse
from app.models.course import Course
from app.dto.user_dto import UserDTO
from app.services import department_service
from app.models.user import TEACHER
from werkzeug.security import generate_password_hash, check_password_hash
from app.models.notification import Notification


def get_all(userDTO: UserDTO):
    try:
        query = sa.select(User)
        conditions = []
        if userDTO.role is not None:
            conditions.append(User.role == userDTO.role)

        if userDTO.is_fired is not None:
            conditions.append(User.is_fired == userDTO.is_fired)

        current_app.logger.info(f"условия {conditions}")

        if conditions:
            query = query.where(sa.and_(*conditions))
        query = query.order_by(User.full_name)
        return db.session.execute(query).scalars().all()
    except Exception as e:
        current_app.logger.error(e)
        raise Exception('Ошибка при получении пользователей')


def get_all_paginated(page: int, userDTO: UserDTO):
    try:
        query = sa.select(User)
        conditions = []
        if userDTO.role is not None:
            conditions.append(User.role == userDTO.role)

        if userDTO.is_fired is not None:
            conditions.append(User.is_fired == userDTO.is_fired)

        if userDTO.full_name is not None and len(userDTO.full_name) == 0:
            userDTO.full_name = None

        if userDTO.username is not None and len(userDTO.username) == 0:
            userDTO.username = None

        if userDTO.full_name is not None:
            conditions.append(sa.func.lower(User.full_name).like(
                f'%{userDTO.full_name.lower()}%'))

        if userDTO.username is not None:
            conditions.append(sa.func.lower(User.username).like(
                f'%{userDTO.username.lower()}%'))

        current_app.logger.info(f"условия {conditions}")

        if conditions:
            query = query.where(sa.and_(*conditions))
        query = query.order_by(User.full_name)
        return db.paginate(query, page=page, per_page=current_app.config['USERS_PER_PAGE'], error_out=False)
    except Exception as e:
        current_app.logger.error(e)
        raise Exception('Ошибка при получении пользователей')


def get_by_id(id: int):
    try:
        res = db.session.get(User, id)
        if res is None:
            raise ValueError(f'Пользователь с id = {id} не существует')
        return res
    except ValueError as e:
        current_app.logger.error(e)
        raise
    except Exception as e:
        current_app.logger.error(e)
        raise Exception('Ошибка при получении пользователя по id')


def get_by_username(username: str):
    try:
        res = db.session.execute(sa.select(User).where(
            User.username == username)).scalar_one_or_none()
        if res is None:
            raise ValueError(f'Пользователь с именем {username} не существует')
        return res
    except ValueError as e:
        current_app.logger.error(e)
        raise
    except Exception as e:
        current_app.logger.error(e)
        raise Exception(
            f'Ошибка при получении пользователя по имени пользователя')


def create(userDTO: UserDTO):
    try:
        user = User(
            username=userDTO.username,
            full_name=userDTO.full_name,
            password_hash=generate_password_hash(userDTO.password),
            role=userDTO.role,
        )
        db.session.add(user)
        db.session.commit()
    except sa.exc.IntegrityError as e:
        db.session.rollback()
        current_app.logger.error(e)
        raise ValueError(
            f'Пользователь с именем {userDTO.username} уже существует')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        raise Exception(f'Ошибка при создании пользователя')


def check_password(username: str, password: str):
    try:
        user = get_by_username(username)
        res = check_password_hash(user.password_hash, password)
        if not res:
            raise WrongPasswordError('Неверный пароль')
        if user.is_fired:
            raise FiredError('Пользователь заблокирован')
        return user
    except ValueError as e:
        current_app.logger.error(e)
        raise
    except WrongPasswordError as e:
        current_app.logger.error(e)
        raise
    except FiredError as e:
        current_app.logger.error(e)
        raise
    except Exception as e:
        current_app.logger.error(e)
        raise Exception('Ошибка при проверке пароля')


def update(userDTO: UserDTO):
    try:
        record = get_by_id(userDTO.id)
        record.username = userDTO.username
        record.full_name = userDTO.full_name
        if userDTO.password:
            record.password_hash = generate_password_hash(userDTO.password)
        db.session.commit()
    except ValueError as e:
        current_app.logger.error(e)
        raise
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        raise Exception('Ошибка при обновлении пользователя')


def delete(id: int) -> bool:
    try:
        user = get_by_id(id)
        db.session.delete(user)
        db.session.commit()
    except ValueError as e:
        current_app.logger.error(e)
        raise
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        raise Exception('Ошибка при удалении пользователя')


def fire(id: int):
    try:
        record = get_by_id(id)
        record.is_fired = not record.is_fired
        if record.is_fired:
            close_user_sessions(id)
        db.session.commit()
    except ValueError as e:
        current_app.logger.error(e)
        raise
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        raise Exception('Ошибка при увольнении пользователя')


def add_to_department(user_id: int, department_id: int):
    try:
        user = get_by_id(user_id)
        if user.role != TEACHER:
            raise ValueError('Нельзя назначить сотрудника на кафедру')
        department = department_service.get_by_id(department_id)
        user.departments.add(department)
        db.session.commit()
    except ValueError as e:
        current_app.logger.error(e)
        raise
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        raise Exception('Ошибка при добавлении пользователя на кафедру')


def remove_from_department(user_id: int, department_id: int):
    try:
        current_app.logger.info('Удаление преподавателя с кафедры')
        user = get_by_id(user_id)
        if user.role != TEACHER:
            raise ValueError('Нельзя убрать сотрудника с кафедры')
        department = department_service.get_by_id(department_id)
        user.departments.remove(department)
        db.session.commit()
    except ValueError as e:
        current_app.logger.error(e)
        raise
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        raise Exception('Ошибка при удалении пользователя с кафедры')


def get_departments(userDTO: UserDTO):
    try:
        user = None
        if userDTO.id is not None:
            user = get_by_id(userDTO.id)
        else:
            user = get_by_username(userDTO.name)
        return db.session.scalars(user.departments.select()).all()
    except ValueError as e:
        current_app.logger.error(e)
        raise
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        raise Exception('Ошибка при получении кафедр пользователя')


def get_notifications(page: int, only_new, user: User):
    try:
        query = user.notifications.select()
        if only_new:
            query = query.where(Notification.has_read == False)
        query = query.order_by(sa.asc(Notification.has_read),
                               sa.desc(Notification.time_sent))
        return db.paginate(query, page=page, per_page=current_app.config['NOTIFICATIONS_PER_PAGE'], error_out=False)
    except Exception as e:
        current_app.logger.error(e)
        raise Exception('Ошибка при получении сообщений пользователя')


def get_courses(page: int, approved: bool, user: User):
    try:
        query = user.courses.select().where(TeacherCourse.date_approved.is_(None))
        if approved:
            query = query.where(TeacherCourse.date_approved is not None)
        query = query.order_by(Course.name)
        return db.paginate(query, page=page, per_page=current_app.config['COURSES_PER_PAGE'], error_out=False)
    except Exception as e:
        current_app.logger.error(e)
        raise Exception('Ошибка при получении курсов пользователя')


def get_users_sessions(user_id):
    try:
        pattern = f'session:{user_id}:*'

        r = current_app.config['SESSION_REDIS']
        keys = r.keys(pattern)

        return keys
    except Exception as e:
        current_app.logger.info(e)
        raise Exception('Неизвестная ошибка')


def close_user_session(session_id):
    try:
        r = current_app.config['SESSION_REDIS']
        r.delete(session_id)
        return True
    except Exception as e:
        current_app.logger.info(e)
        raise Exception('Неизвестная ошибка')


def close_user_sessions(user_id):
    try:
        r = current_app.config['SESSION_REDIS']
        keys = get_users_sessions(user_id)
        if keys:
            r.delete(*keys)
        return len(keys)
    except Exception as e:
        current_app.logger.info(e)
        raise Exception('Неизвестная ошибка')


def get_token(user_id, expires_in=3600):
    try:
        now = datetime.now()
        user = get_by_id(user_id)
        if user.token and user.token_expiration > now + timedelta(seconds=60):
            return user.token
        user.token = secrets.token_hex(16)
        user.token_expiration = now + timedelta(seconds=expires_in)
        db.session.commit()
        return user.token
    except ValueError as e:
        current_app.logger.error(e)
        raise
    except Exception as e:
        db.session.rollback()
        raise Exception('Неизвестная ошибка')


def revoke_token(user_id):
    try:
        user = get_by_id(user_id)
        user.token_expiration = datetime.now() - timedelta(seconds=1)
        db.session.commit()
        return user
    except ValueError as e:
        current_app.logger.error(e)
        raise
    except Exception as e:
        db.session.rollback()
        raise Exception('Неизвестная ошибка')


def check_token(token):
    try:
        user = db.session.scalar(sa.select(User).where(User.token == token))
        if user is None or user.token_expiration < datetime.now():
            raise ValueError(f'Пользователь с  тоеном = {token} не существует')
        return user
    except ValueError as e:
        current_app.logger.error(e)
        raise
    except Exception as e:
        current_app.logger.error(e)
        raise Exception('Ошибка при получении пользователя по токену')
