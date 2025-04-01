from flask_login import current_user
from flask import make_response, render_template


def role_accepted(role):
    def decorator(func):
        def check_role(*args, **kwargs):
            if current_user.role is None or current_user.role != role:
                return make_response(render_template('403.html'), 403)
            return func(args, kwargs)
        return check_role
    return decorator
