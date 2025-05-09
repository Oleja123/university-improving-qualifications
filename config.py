import os

basedir = os.path.abspath(os.path.dirname('__file__'))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'pososamba'
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')
    DEPARTMENTS_PER_PAGE = 3
    NOTIFICATIONS_PER_PAGE = 3
    USERS_PER_PAGE = 3
    COURSES_PER_PAGE = 3
    SERTIFICATES_FOLDER = '/sertificates'
    ALLOWED_EXTENSIONS = { 'pdf' }