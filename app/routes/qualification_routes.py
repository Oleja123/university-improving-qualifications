from flask import render_template, request
from flask_login import login_required

from app.decorators.role_decorator import required_role
from app.models import user
from app.services import course_service, sertificate_service
from app import app


@app.route('/teacher_course/<user_id>/<course_id>')
@login_required
@required_role(role=user.TEACHER)
def teacher_course(user_id, course_id):
    return render_template('teachers_courses/teacher_course.html', title='Курсы преподавателя', teacher_course=sertificate_service.get(user_id, course_id) )
