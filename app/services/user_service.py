from app import db, app
from app.models.user import User
from app.models.department import Department
from app.models.teacher_course import TeacherCourse
from app.models.course import Course
from app.dto.user_dto import UserDTO
from werkzeug.security import generate_password_hash, check_password_hash
from app.models.notification import Notification
import sqlalchemy as sa
from app.models import user
from app.exceptions.wrong_password_error import WrongPasswordError


def get_all_teachers(departments=None):
    try:
        if departments is not None:
            query = query.join(User.departments).where(sa.and_(Department.id.in_(departments), User.role == user.TEACHER)).order_by(Department.name)
        else: 
            query = query.where(User.role == user.TEACHER)
        return db.session.execute(query).scalars().all()
    except Exception as e:
        db.session.rollback()
        app.logger.error(e)
        raise Exception('Неизвестная ошибка')

def get_all_paginated_teachers(page: int, departments=None):
    try:
        query = sa.select(User)
        if departments is not None:
            query = query.join(User.departments).where(sa.and_(Department.id.in_(departments), User.role == user.TEACHER)).order_by(Department.name)
        else:
            query = query.where(User.role == user.TEACHER)
        return db.paginate(query, page=page, per_page=app.config['USERS_PER_PAGE'], error_out=False)
    except Exception as e:
        db.session.rollback()
        app.logger.error(e)
        raise Exception('Неизвестная ошибка')
    
def get_all_fired(departments=None):
    try:
        if departments is not None:
            query = query.join(User.departments).where(sa.and_(Department.id.in_(departments), User.role == user.FIRED)).order_by(Department.name)
        else: 
            query = query.where(User.role == user.FIRED)
        return db.session.execute(query).scalars().all()
    except Exception as e:
        db.session.rollback()
        app.logger.error(e)
        raise Exception('Неизвестная ошибка')

def get_all_paginated_fired(page: int, departments=None):
    try:
        query = sa.select(User)
        if departments is not None:
            query = query.join(User.departments).where(sa.and_(Department.id.in_(departments), User.role == user.FIRED)).order_by(Department.name)
        else:
            query = query.where(User.role == user.FIRED)
        return db.paginate(query, page=page, per_page=app.config['USERS_PER_PAGE'], error_out=False)
    except Exception as e:
        db.session.rollback()
        app.logger.error(e)
        raise Exception('Неизвестная ошибка')
    
def get_all_admins():
    try:
        query = query.where(User.role == user.ADMIN)
        return db.session.execute(query).scalars().all()
    except Exception as e:
        db.session.rollback()
        app.logger.error(e)
        raise Exception('Неизвестная ошибка')

def get_all_paginated_admins(page: int):
    try:
        query = sa.select(User)
        query = query.where(User.role == user.ADMIN)
        return db.paginate(query, page=page, per_page=app.config['USERS_PER_PAGE'], error_out=False)
    except Exception as e:
        db.session.rollback()
        app.logger.error(e)
        raise Exception('Неизвестная ошибка')

def get_by_id(id: int):
    try:
        res = db.session.get(User, id)
        if res is None:
            raise ValueError(f'Пользователь с id = {id} не существует')
        return res
    except ValueError as e:
        db.session.rollback()
        app.logger.error(e)
        raise
    except Exception as e:
        db.session.rollback()
        app.logger.error(e)
        raise Exception('Неизвестная ошибка')


def get_by_username(username: str):
    try:
        res = db.session.execute(sa.select(User).where(User.username == username)).scalar_one_or_none()
        if res is None:
            raise ValueError(f'Пользователь с именем {username} не существует')
        return res
    except ValueError as e:
        db.session.rollback()
        app.logger.error(e)
        raise
    except Exception as e:
        db.session.rollback()
        app.logger.error(e)
        raise Exception(f'Неизвестная ошибка')
    
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
    except ValueError as e:
        db.session.rollback()
        app.logger.error(e)
        raise
    except sa.exc.IntegrityError as e:
        db.session.rollback()
        app.logger.error(e)
        raise ValueError(f'Пользователь с именем {userDTO.name} уже существует')
    except Exception as e:
        db.session.rollback()
        app.logger.error(e)
        raise Exception(f'Неизвестная ошибка при создании кафедры')

def check_password(username, password):
    try:
        user = get_by_username(username)
        res = check_password_hash(user.password_hash, password)
        if not res:
            raise WrongPasswordError('Неверный пароль')
    except ValueError:
        db.session.rollback()
        raise
    except WrongPasswordError as e:
        db.session.rollback()
        app.logger.error(e)
        raise
    except Exception as e:
        db.session.rollback()
        app.logger.error(e)
        raise Exception('Неизвестная ошибка')

def update(userDTO: UserDTO):
    try:
        record = get_by_id(userDTO.id)
        record.username = userDTO.username
        record.full_name = userDTO.name
        if userDTO.password is not None:
            record.password_hash = generate_password_hash(userDTO.password)
        record.role = userDTO.role
        db.session.commit()
    except ValueError:
        db.session.rollback()
        raise
    except Exception as e:
        db.session.rollback()
        app.logger.error(e)
        raise Exception('Неизвестная ошибка')


def delete(id: int) -> bool:
    try:
        user = get_by_id(id)
        db.session.delete(user)
        db.session.commit()
    except ValueError:
        db.session.rollback()
        raise
    except Exception as e:
        db.session.rollback()
        app.logger.error(e)
        raise Exception('Неизвестная ошибка')



def get_departments(userDTO: UserDTO):
    try:
        user = None
        if userDTO.id is not None:
            user = get_by_id(userDTO.id)
        else:
            user = get_by_username(userDTO.name)
        return db.session.scalars(user.departments.select()).all()
    except ValueError:
        db.session.rollback()
        raise
    except Exception as e:
        db.session.rollback()
        app.logger.error(e)
        raise Exception('Неизвестная ошибка')

def get_notifications(page: int, only_new, user: User):
    try:
        query = user.notifications.select()
        if only_new:
            query = query.where(Notification.has_read == True)
        query = query.order_by(sa.desc(Notification.time_sent))
        return db.paginate(query, page=page, per_page=app.config['NOTIFICATIONS_PER_PAGE'], error_out=False)
    except Exception:
        db.session.rollback()
        app.logger.error(e)
        raise Exception('Неизвестная ошибка')

def get_courses(page: int, approved: bool, user: User):
    try:
        query = user.courses.select().where(TeacherCourse.date_approved is None)
        if approved:
            query = query.where(TeacherCourse.date_approved is not None)
        query = query.order_by(Course.name)
        return db.paginate(query, page=page, per_page=app.config['COURSES_PER_PAGE'], error_out=False)
    except Exception:
        db.session.rollback()
        app.logger.error(e)
        raise Exception('Неизвестная ошибка')
