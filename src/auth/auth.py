import os
from functools import wraps
import jwt
from ..dao import AccessTokenDao

from .tokens import Access, Refresh

from ..errors.AuthError import AuthError


def bearer(f):
    """Determines if the Access Token is valid
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token_dao = AccessTokenDao()
        token = Access.get_token()

        try:
            jwt.decode(
                token,
                os.environ["SECRET"],
                algorithms=["HS256"],
            )
            token_dao.search(token)

        except jwt.ExpiredSignatureError:
            raise AuthError({"code": "token_expired",
                            "description": "token is expired"}, 401)

        except jwt.InvalidTokenError:
            raise AuthError({"code": "invalid_token_error",
                             "description": "invalid token"}, 401)

        except Exception as err:
            print(err)
            raise AuthError({"code": "invalid_header",
                            "description":
                                "Unable to parse authentication"
                                " token."}, 401)

        return f(*args, **kwargs)
    return decorated


def refresh(token):
    """Refresh strategy"""

    user_id = Refresh.verify(token)
    Refresh.invalidate(token)

    refresh_token = Refresh.generate(user_id)
    access_token = Access.generate(user_id)

    return refresh_token, access_token

