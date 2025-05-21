from flask import abort

from app.api import bp
from app.api.auth import basic_auth
from app.services import user_service
from app.api.auth import token_auth
from app import csrf

@bp.route('/tokens', methods=['POST'])
@csrf.exempt
@basic_auth.login_required
def get_token():
    try:
        token = user_service.get_token(basic_auth.current_user().id)
        return {'token': token, 'id': basic_auth.current_user().id}
    except ValueError as e:
        abort(404)
    except Exception as e :
        abort(500)


@bp.route('/tokens', methods=['DELETE'])
@csrf.exempt
@token_auth.login_required
def revoke_token():
    user_service.revoke_token(token_auth.current_user().id)
    return '', 204