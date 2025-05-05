from app import app, db
from werkzeug.utils import secure_filename
from app.services import user_service, course_service
import os

from app.models.teacher_course import TeacherCourse


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def upload_sertificate(user_id, course_id, file):
    if file.filename == '':
        raise ValueError('Нет выбранного файла')
    if not allowed_file(file.filename):
        raise ValueError('Некорректное расширение файла')
    filename = secure_filename(file.filename)
    user_path = os.path.join(app.config['UPLOAD_FOLDER'], user_id, course_id)
    os.makedirs(user_path, exist_ok=True)
    filepath = os.path.join(user_path, filename)
    file.save(filepath)
    res = get(user_id, course_id)
    res.sertificate_path = filepath
    db.session.commit()


def get(user_id, course_id):
    res = db.session.get(TeacherCourse, (user_id, course_id))
    if res is None:
        teacher = user_service.get_by_id(user_id)
        course = course_service.get_by_id(course_id)
        db.session.add(TeacherCourse(teacher=teacher, course=course))
        db.session.commit()
        res = db.session.get(TeacherCourse, (user_id, course_id))
    return res

