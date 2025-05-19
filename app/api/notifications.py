from app.api import bp


@bp.route('/notifications/<int:id>', methods=['GET'])
def get_notification(id):
    pass