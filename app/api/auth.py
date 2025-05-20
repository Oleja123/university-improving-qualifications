from flask import abort, current_app
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth

from app.api.errors import error_response
from app.exceptions.fired_error import FiredError
from app.exceptions.wrong_password_error import WrongPasswordError
from app.services import user_service


basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth()


@basic_auth.verify_password
def verify_password(username, password):
    try:
        user = user_service.check_password(username, password)
        return user
    except ValueError as e:
        abort(400)
    except WrongPasswordError as e:
        abort(401)
    except FiredError as e:
        abort(403)
    except Exception as e:
        abort(500)


@basic_auth.error_handler
def basic_auth_error(status):
    current_app.logger.info(status)
    return error_response(status)


@token_auth.verify_token
def verify_token(token):
    try:
        return user_service.check_token(token) if token else None
    except ValueError as e:
        abort(401)
    except Exception as e:
        abort(500)


@token_auth.error_handler
def token_auth_error(status):
    return error_response(status)
