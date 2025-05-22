from functools import wraps

from flask import abort

from app.api.auth import token_auth
from app.models.user import ADMIN


def required_role(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not token_auth.current_user().role == role:
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def user_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = kwargs.get('user_id')

        if not token_auth.current_user().role == ADMIN and \
            (user_id is None or str(user_id) != str(str(token_auth.current_user().id))):
            abort(403)
            
        return f(*args, **kwargs)
    return decorated_function