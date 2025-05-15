from app import app
from flask import render_template
from flask_login import login_required

@app.route('/')
@app.route('/index')
@login_required
def index():
    return render_template('index.html')

import app.routes.faculty_routes, app.routes.department_routes, app.routes.course_type_routes, app.routes.course_routes, app.routes.user_routes, app.routes.qualification_routes
import app.routes.notification_routes, app.routes.reports_routes, app.routes.auth_routes
