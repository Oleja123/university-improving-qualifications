import json
import os

from flask import Response, abort, current_app, request, send_from_directory

from app.api import bp
from app.exceptions.role_error import RoleError
from app.services import course_service, sertificate_service, user_service
from app.services.to_json_collecion import to_json_collection
from app.models.user import TEACHER
from app.api.auth import token_auth
from app.api.decorators import user_required


@bp.route('/users/<int:user_id>', methods=['GET'])
@token_auth.login_required
@user_required
def get_user(user_id):
    try:
        return Response(
            json.dumps(user_service.get_by_id(user_id).to_dict(), ensure_ascii=False),
            mimetype='application/json; charset=utf-8'
        )
    except ValueError as e:
        current_app.logger.error(e)
        abort(404)
    except Exception as e:
        current_app.logger.error(e)
        abort(500)

@bp.route('/users/<int:user_id>/notifications', methods=['GET'])
@token_auth.login_required
@user_required
def get_user_notifications(user_id):
    try:
        user = user_service.get_by_id(user_id)
        page = request.args.get('page', 1, type=int)
        res = to_json_collection(user_service.get_notifications(page=page, only_new=False, user=user), 
                                 'api.get_user_notifications', user_id=user_id)
        return Response(
            json.dumps(
                res,
                ensure_ascii=False
            ),
            mimetype='application/json; charset=utf-8'
        )
    except ValueError as e:
        current_app.logger.error(e)
        abort(404)
    except Exception as e:
        current_app.logger.error(e)
        abort(500)


@bp.route('/users/<int:user_id>/courses', methods=['GET'])
@token_auth.login_required
@user_required
def get_teacher_courses(user_id):
    try:
        user = user_service.get_by_id(user_id)
        page = request.args.get('page', 1, type=int)
        res = to_json_collection(sertificate_service.get_user_courses(page=page, user_id=user_id), 
                                 'api.get_teacher_courses', user_id=user_id)
        return Response(
            json.dumps(
                res,
                ensure_ascii=False
            ),
            mimetype='application/json; charset=utf-8'
        )
    except ValueError as e:
        current_app.logger.error(e)
        abort(404)
    except Exception as e:
        current_app.logger.error(e)
        abort(500)
    

@bp.route('/users/<int:user_id>/courses/<int:course_id>', methods=['GET'])
@token_auth.login_required
@user_required
def get_teacher_course(user_id, course_id):
    try:
        user = user_service.get_by_id(user_id)
        if user.role != TEACHER:
            raise RoleError('У сотрудника не может быть курсов')
        course = course_service.get_by_id(course_id)
        return Response(
            json.dumps(sertificate_service.get(user_id, course_id).to_dict(), ensure_ascii=False),
            mimetype='application/json; charset=utf-8'
        )
    except ValueError as e:
        current_app.logger.error(e)
        abort(404)
    except Exception as e:
        current_app.logger.error(e)
        abort(500)


@bp.route('/users/<int:user_id>/courses/<int:course_id>/download', methods=['GET'])
@token_auth.login_required
@user_required
def download_teacher_course(user_id, course_id):
    try:
        user_path = sertificate_service.make_path(str(user_id), str(course_id))
        current_app.logger.info(user_path)
        file = os.listdir(user_path)[0]
        current_app.logger.info(file)
        return send_from_directory(user_path, 
                                   file, 
                                   as_attachment=True,
                                   mimetype='application/pdf')
    except ValueError as e:
        current_app.logger.error(e)
        abort(404)
    except Exception as e:
        current_app.logger.error(e)
        abort(500)
