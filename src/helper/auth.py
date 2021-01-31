import os
from flask import request
from functools import wraps
import jwt

from ..errors.AuthError import AuthError


def get_token_auth_header():
    """Obtains the Access Token from the Authorization Header
    """
    auth = request.get_json()
    try:
        token = auth["authorization"]
    except Exception:
        raise AuthError({"code": "authorization_token_missing",
                        "description":
                            "Authorization token is expected"}, 401)

    return token


def requires_auth(f):
    """Determines if the Access Token is valid
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = get_token_auth_header()

        try:
            jwt.decode(
                token,
                os.environ["SECRET"],
                algorithms=["HS256"],
            )
        except jwt.ExpiredSignatureError:
            raise AuthError({"code": "token_expired",
                            "description": "token is expired"}, 401)

        except Exception:
            raise AuthError({"code": "invalid_header",
                            "description":
                                "Unable to parse authentication"
                                " token."}, 401)

        return f(*args, **kwargs)
    return decorated
