import sqlalchemy as sa
import sqlalchemy.orm as so
from app import create_app, db
from app.models.course import Course
from app.models.department import Department
from app.models.faculty import Faculty
from app.models.teacher_course import TeacherCourse
from app.models.user import User


app = create_app()


@app.shell_context_processor
def make_shell_context():
    return {'sa': sa, 'so': so, 'db': db, 'User': User,
            'Course': Course, 'Faculty': Faculty, 
            'Department': Department, 'TeacherCourse': TeacherCourse, 
            'r': app.config['SESSION_REDIS']}
