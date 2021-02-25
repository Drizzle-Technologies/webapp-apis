from ..errors.InvalidArguementError import InvalidArgumentError

from werkzeug.security import check_password_hash
from flask import request


def calculate_max_people(area):
    """Calculates the max number of people allowed in a building"""
    stadard_capacity = area*2

    # This numbers are defined for the 4th level of flexibilization of São Paulo state quarantine
    pandemic_capacity = stadard_capacity * 0.6
    return int(pandemic_capacity)


def verify_user(user):
    if not user:
        raise InvalidArgumentError({"code": "InvalidArgumentError",
                                    "description": "This user does not exist."}, 404)


def verify_password(user, password):
    """Method validates a password by comparing the stored hash to the input password."""
    if not check_password_hash(user.password, password):
        raise InvalidArgumentError({"code": "InvalidArgumentError",
                                    "description": "Password incorrect."}, 400)


def get_token():
    req = request.headers.get("Authorization", None)
    token = req.split()[1]

    return token


def is_not_logged_in(session):
    """Returns whether the user is logged in or not"""
    return 'logged_in' not in session or session['logged_in'] is None
