import json

from flask import Response, abort

from app.api import bp
from app import csrf
from app.models.user import ADMIN
from app.services import notification_service
from app.api.auth import token_auth


@bp.route('/notifications/<int:id>', methods=['GET'])
@token_auth.login_required
def get_notification(id):
    try:
        res = notification_service.get_by_id(id)
        if token_auth.current_user().role != ADMIN and \
            token_auth.current_user().id != res.user_id:
            abort(403)
        return Response(
            json.dumps(res.to_dict(), ensure_ascii=False),
            mimetype='application/json; charset=utf-8'
        )
    except ValueError as e:
        abort(404)
    except Exception as e:
        abort(500)

@bp.route('/notifications/<int:id>/read', methods=['PUT'])
@csrf.exempt
@token_auth.login_required
def read_notification(id):
    try:
        res = notification_service.get_by_id(id)
        if token_auth.current_user().role != ADMIN and \
            token_auth.current_user().id != res.user_id:
            abort(403)
        notification_service.read_message(id)
        return Response(
            json.dumps(notification_service.get_by_id(id).to_dict(), ensure_ascii=False),
            mimetype='application/json; charset=utf-8'
        )
    except ValueError as e:
        abort(404)
    except Exception as e:
        abort(500)
    

@bp.route('/notifications/<int:id>/delete', methods=['DELETE'])
@csrf.exempt
@token_auth.login_required
def delete_notification(id):
    try:
        res = notification_service.get_by_id(id)
        if token_auth.current_user().role != ADMIN and \
            token_auth.current_user().id != res.user_id:
            abort(403)
        notification_service.delete(id)
        return '', 204
    except ValueError as e:
        abort(404)
    except Exception as e:
        abort(500)