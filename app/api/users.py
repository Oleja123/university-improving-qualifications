import json
import os

from flask import Response, abort, current_app, request, send_from_directory, url_for

from app.api import bp
from app.exceptions.role_error import RoleError
from app.services import course_service, sertificate_service, user_service
from app.services.to_json_collecion import to_json_collection
from app.models.user import TEACHER
from app.api.auth import token_auth
from app.api.decorators import user_required, only_admin
from app.models import user
from app.dto.user_dto import UserDTO
from app import csrf


@bp.route('/users/<int:user_id>', methods=['GET'])
@token_auth.login_required
@user_required
def get_user(user_id):
    try:
        return Response(
            json.dumps(user_service.get_by_id(
                user_id).to_dict(), ensure_ascii=False),
            mimetype='application/json; charset=utf-8'
        )
    except ValueError as e:
        current_app.logger.error(e)
        abort(404)
    except Exception as e:
        current_app.logger.error(e)
        abort(500)


@bp.route('/users', methods=['GET'])
@token_auth.login_required
@only_admin
def get_users():
    try:
        page = request.args.get('page', 1, type=int)
        username = request.args.get('username', None, type=str)
        full_name = request.args.get('full_name', None, type=str)
        res = to_json_collection(user_service.get_all_paginated(page=page,
                                                                userDTO=UserDTO(username=username,
                                                                                full_name=full_name)),
                                 'api.get_users')
        return Response(
            json.dumps(
                res,
                ensure_ascii=False
            ),
            mimetype='application/json; charset=utf-8'
        )
    except Exception as e:
        current_app.logger.error(e)
        abort(500)


@bp.route('/users/<int:user_id>/revoke_token', methods=['PUT'])
@csrf.exempt
@token_auth.login_required
@only_admin
def revoke_user_token(user_id):
    try:
        res = user_service.revoke_token(user_id)
        return Response(
            json.dumps(res.to_dict(), ensure_ascii=False),
            mimetype='application/json; charset=utf-8'
        )
    except ValueError as e:
        abort(404)
    except Exception as e:
        abort(500)


@bp.route('/users/<int:user_id>/sessions', methods=['GET'])
@token_auth.login_required
@only_admin
def get_user_sessions(user_id):
    try:
        res = [i.decode() for i in user_service.get_users_sessions(user_id)]
        data = {
            'items': [item for item in res],
            '_meta': {
                'total_items': len(res)
            },
            '_links': {
                'self': url_for('api.get_user_sessions', user_id=user_id),
                'close': url_for('api.get_user_sessions', user_id=user_id) + '/close',
            }
        }
        return Response(
            json.dumps(
                data,
                ensure_ascii=False
            ),
            mimetype='application/json; charset=utf-8'
        )
    except Exception as e:
        current_app.logger.error(e)
        abort(500)


@bp.route('/users/<int:user_id>/sessions/close', methods=['DELETE'])
@csrf.exempt
@token_auth.login_required
@only_admin
def close_user_sessions(user_id):
    try:
        user_service.close_user_sessions(user_id)
        return '', 204
    except Exception as e:
        current_app.logger.error(e)
        abort(500)


@bp.route('/users/<int:user_id>/sessions/close/<session_id>', methods=['DELETE'])
@csrf.exempt
@token_auth.login_required
@only_admin
def close_user_session(user_id, session_id):
    try:
        user_service.close_user_session(session_id)
        return '', 204
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
            json.dumps(sertificate_service.get(
                user_id, course_id).to_dict(), ensure_ascii=False),
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
        if not os.path.exists(user_path):
            raise ValueError('Сертификат не загружен')
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
