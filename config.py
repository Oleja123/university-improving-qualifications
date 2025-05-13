import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname('__file__'))
load_dotenv()


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY') or 'pososamba'
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')
    DEPARTMENTS_PER_PAGE = 3
    NOTIFICATIONS_PER_PAGE = 3
    USERS_PER_PAGE = 3
    COURSES_PER_PAGE = 3
    UPLOAD_FOLDER = 'sertificates'
    ALLOWED_EXTENSIONS = { 'pdf' }