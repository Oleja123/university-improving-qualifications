from flask import app, request
from flask_login import login_required

from app.decorators.role_decorator import required_role
from app.models import user
from app.services import course_service


@app.route('/courses')
@login_required
@required_role(role=user.ADMIN)
def courses():
    page = request.args.get('page', 1, type=int)
    course_type = request.args.get('course_type_id', None, type=int)
    is_included = request.args.get('is_included', None, type=str)
    if is_included == '':
        is_included=None
    if is_included is not None and is_included == 'True':
        is_included = True
    if is_included is not None and is_included == 'False':
        is_included = False
    if course_type is not None:
        course_type = [course_type]
    courses = course_service.get_all_paginated(page, is_included, course_type)
    course_types = course_type_service.get_all()
    return render_template('courses/courses.html', title='Курсы', courses=courses, course_types=course_types)
