import json

from flask import Response, abort, current_app, jsonify, request
from app.api import bp
from app.api.errors import bad_request, error_response, handle_exception
from app.services import sertificate_service, user_service
from app.services.to_json_collecion import to_json_collection


@bp.route('/users/<int:id>', methods=['GET'])
def get_user(id):
    try:
        return Response(
            json.dumps(user_service.get_by_id(id).to_dict(), ensure_ascii=False),
            mimetype='application/json; charset=utf-8'
        )
    except ValueError as e:
        return bad_request(str(e))
    except Exception as e:
        return error_response(500, str(e))

@bp.route('/users/<int:id>/notifications', methods=['GET'])
def get_user_notifications(id):
    try:
        user = user_service.get_by_id(id)
        page = request.args.get('page', 1, type=int)
        res = to_json_collection(user_service.get_notifications(page=page, only_new=False, user=user), 
                                 'api.get_user_notifications', id=id)
        return Response(
            json.dumps(
                res,
                ensure_ascii=False
            ),
            mimetype='application/json; charset=utf-8'
        )
    except ValueError as e:
        return bad_request(str(e))
    except Exception as e:
        return error_response(500, str(e))


@bp.route('/users/<int:id>/sertificates', methods=['GET'])
def get_user_sertificates(id):
    try:
        user = user_service.get_by_id(id)
        page = request.args.get('page', 1, type=int)
        res = to_json_collection(sertificate_service.get_user_courses(page=page, user_id=id), 
                                 'api.get_user_sertificates', id=id)
        return Response(
            json.dumps(
                res,
                ensure_ascii=False
            ),
            mimetype='application/json; charset=utf-8'
        )
    except ValueError as e:
        return bad_request(str(e))
    except Exception as e:
        return error_response(500, str(e))

