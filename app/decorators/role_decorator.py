from flask_login import current_user
from flask import make_response, render_template


def role_accepted(role):
    def decorator(func):
        def check_role(*args, **kwargs):
            if current_user.role is None or current_user.role.name != role:
                return make_response(render_template('403.html'), 403)
            if len(args) != 0 and len(kwargs) != 0:
                return func(args, kwargs)
            if len(args) != 0:
                return func(args)
            if len(kwargs) != 0:
                return func(kwargs)
            return func()
        return check_role
    return decorator
