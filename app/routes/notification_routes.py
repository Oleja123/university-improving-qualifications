import os
from flask import flash, jsonify, redirect, render_template, request, send_from_directory, url_for
from flask_login import current_user, login_required

from app.decorators.role_decorator import required_role
from app.services import notification_service, user_service
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


@app.route('/notifications/<user_id>')
@login_required
def notifications(user_id):
    page = request.args.get('page', 1, type=int)
    notifications = user_service.get_notifications(page, only_new=False, user=current_user)
    return render_template('notifications/notifications.html', title='Уведомления', notifications=notifications)


@app.route('/notifications/delete/<notification_id>', methods=['DELETE'])
@login_required
def delete_notification(notification_id):
    try:
        notification_service.delete(notification_id)
        return jsonify({'success': True })
    except Exception as ex:
        flash(ex)

@app.route('/notifications/read/<notification_id>', methods=['POST'])
@login_required
def read_notification(notification_id):
    try:
        notification_service.read_message(notification_id)
        return jsonify({'success': True })
    except Exception as ex:
        flash(ex)