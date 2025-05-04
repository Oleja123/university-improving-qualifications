from app import db, app
from app.models.user import User
from app.models.course import Course
from app.models.teacher_course import TeacherCourse
from app.dto.user_dto import UserDTO
from werkzeug.security import generate_password_hash, check_password_hash
from app.models.notification import Notification
import sqlalchemy as sa


def get_all():
    return db.session.execute(sa.select(User)).scalars().all()


def get_by_id(id: int):
    return db.session.get(User, id)


def get_by_username(username: str):
    return db.session.execute(sa.select(User).where(User.username == username)).scalar_one_or_none()

def create(userDTO: UserDTO):
    user = User(
        username=userDTO.username,
        full_name=userDTO.full_name,
        password_hash=generate_password_hash(userDTO.password),
        role=userDTO.role,
    )
    db.session.add(user)
    db.session.commit()

def check_password(username, password):
    user = get_by_username(username)
    return check_password_hash(user.password_hash, password)

def update(userDTO: UserDTO):
    record = get_by_id(userDTO.id)
    if record is None:
        return False
    record.username = userDTO.username
    record.full_name = userDTO.name
    if userDTO.password is not None:
        record.password_hash = generate_password_hash(userDTO.password)
    record.role = userDTO.role
    db.session.commit()
    return True


def delete(id: int) -> bool:
    user = get_by_id(id)
    if (user is None):
        return False
    db.session.delete(user)
    db.session.commit()
    return True


def get_departments(userDTO: UserDTO):
    user = None
    if userDTO.id is not None:
        user = get_by_id(userDTO.id)
    else:
        user = get_by_username(userDTO.name)
    return db.session.scalars(user.departments.select()).all()

def get_notifications(page: int, only_new, user: User):
    query = user.notifications.select()
    if only_new:
        query = query.where(Notification.has_read == True)
    return db.paginate(query, page=page, per_page=app.config['NOTIFICATIONS_PER_PAGE'], error_out=False)

def get_courses(page: int, approved: bool, user: User):
    query = user.courses.select().where(TeacherCourse.date_approved is None)
    if approved:
        query = query.where(TeacherCourse.date_approved is not None)
    return db.paginate(query, page=page, per_page=app.config['COURSES_PER_PAGE'], error_out=False)
