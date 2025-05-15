from app import app
from flask import render_template
from flask_login import login_required
from app.main import bp

@bp.route('/')
@bp.route('/index')
@login_required
def index():
    return render_template('index.html')

import app.main.routes.faculty_routes, app.main.routes.department_routes, app.main.routes.course_type_routes
import app.main.routes.course_routes, app.main.routes.user_routes, app.main.routes.qualification_routes
import app.main.routes.notification_routes, app.main.routes.reports_routes
