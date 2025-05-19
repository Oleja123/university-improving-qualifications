import json

from flask import Response, abort

from app.api import bp
from app import csrf
from app.services import notification_service


@bp.route('/notifications/<int:id>', methods=['GET'])
def get_notification(id):
    try:
        return Response(
            json.dumps(notification_service.get_by_id(
                id).to_dict(), ensure_ascii=False),
            mimetype='application/json; charset=utf-8'
        )
    except ValueError as e:
        abort(404)
    except Exception as e:
        abort(500)

@bp.route('/notifications/<int:id>/read', methods=['PUT'])
@csrf.exempt
def read_notification(id):
    try:
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
def delete_notification(id):
    try:
        notification_service.delete(id)
        return '', 204
    except ValueError as e:
        abort(404)
    except Exception as e:
        abort(500)