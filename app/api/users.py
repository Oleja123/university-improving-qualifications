import json
import os

from flask import Response, abort, current_app, jsonify, request, send_from_directory
from app.api import bp
from app.api.errors import bad_request, error_response, handle_exception
from app.exceptions.role_error import RoleError
from app.services import course_service, sertificate_service, user_service
from app.services.to_json_collecion import to_json_collection
from app.models.user import TEACHER


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


@bp.route('/users/<int:id>/courses', methods=['GET'])
def get_teacher_courses(id):
    try:
        user = user_service.get_by_id(id)
        page = request.args.get('page', 1, type=int)
        res = to_json_collection(sertificate_service.get_user_courses(page=page, user_id=id), 
                                 'api.get_teacher_courses', id=id)
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
    

@bp.route('/users/<int:teacher_id>/courses/<int:course_id>', methods=['GET'])
def get_teacher_course(teacher_id, course_id):
    try:
        user = user_service.get_by_id(teacher_id)
        if user.role != TEACHER:
            raise RoleError('У сотрудника не может быть курсов')
        course = course_service.get_by_id(course_id)
        return Response(
            json.dumps(sertificate_service.get(teacher_id, course_id).to_dict(), ensure_ascii=False),
            mimetype='application/json; charset=utf-8'
        )
    except ValueError as e:
        return bad_request(str(e))
    except Exception as e:
        return error_response(500, str(e))


@bp.route('/users/<int:teacher_id>/courses/<int:course_id>/download', methods=['GET'])
def download_teacher_course(teacher_id, course_id):
    try:
        user_path = sertificate_service.make_path(str(teacher_id), str(course_id))
        current_app.logger.info(user_path)
        file = os.listdir(user_path)[0]
        current_app.logger.info(file)
        return send_from_directory(user_path, file, as_attachment=True)
    except Exception as e:
        current_app.logger.info(e)
        return jsonify({"error": str(e)}), 500
