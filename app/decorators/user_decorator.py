
from functools import wraps

from flask import abort
from flask_login import current_user


def user_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = kwargs.get('user_id')
        
        if user_id and str(current_user.id) != str(user_id):
            abort(403)
            
        return f(*args, **kwargs)
    return decorated_function