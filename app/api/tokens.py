from app.api import bp
from app.api.auth import basic_auth
from app.services import user_service
from app import csrf

@bp.route('/tokens', methods=['POST'])
@basic_auth.login_required
@csrf.exempt
def get_token():
    token = user_service.get_by_id(basic_auth.current_user().id)
    return {'token': token}
