from flask import jsonify
from . import bp
from .AuthError import AuthError
from .InvalidArguementError import InvalidArgumentError


@bp.app_errorhandler(InvalidArgumentError)
def handle_auth_error(error):
    response = jsonify(error.error)
    response.status_code = error.status
    return response


@bp.app_errorhandler(AuthError)
def handle_auth_error(error):
    response = jsonify(error.error)
    response.status_code = error.status
    return response
