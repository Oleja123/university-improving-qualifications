from flask import jsonify, render_template, request
from flask_login import current_user, login_required

from app.decorators.role_decorator import required_role
from app.decorators.user_decorator import user_required
from app.services import notification_service, user_service
from app.main import bp


@bp.route('/get_messages_count/<user_id>')
@login_required
def get_messages_count(user_id):
    try:
        res = notification_service.get_user_notifications_count(user_id)
        return jsonify({'cnt': res})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route('/notifications/<user_id>')
@login_required
@user_required
def notifications(user_id):
    page = request.args.get('page', 1, type=int)
    notifications = user_service.get_notifications(
        page, only_new=False, user=current_user)
    return render_template('notifications/notifications.html', title='Уведомления', notifications=notifications)


@bp.route('/notifications/<user_id>/delete/<notification_id>', methods=['DELETE'])
@login_required
@user_required
def delete_notification(user_id, notification_id):
    try:
        notification_service.delete(notification_id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route('/notifications/<user_id>/read/<notification_id>', methods=['POST'])
@login_required
@user_required
def read_notification(user_id, notification_id):
    try:
        notification_service.read_message(notification_id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
