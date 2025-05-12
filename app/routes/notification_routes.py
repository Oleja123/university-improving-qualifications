import os
from flask import flash, jsonify, redirect, render_template, request, send_from_directory, url_for
from flask_login import login_required

from app.decorators.role_decorator import required_role
from app.forms import TeachersCoursesForm, UploadForm
from app.models import user
from app.services import course_service, notification_service, sertificate_service, user_service
from app import app


@app.route('/get_messages_count/<user_id>')
@login_required
def get_messages_count(user_id):
    try:
        res = notification_service.get_user_notifications_count(user_id)
        return jsonify({'cnt': res})
    except Exception as e:
        app.logger.info(e)
        flash('Ошибка при получении уведомления')