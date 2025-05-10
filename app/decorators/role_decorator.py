from functools import wraps

from flask import abort, make_response, render_template, session
from flask_login import current_user
from app import app


def required_role(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.role == role:
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator