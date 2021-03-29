import os

from flask import request

from datetime import datetime, timedelta

import jwt

from ..errors.AuthError import AuthError
from ..errors.InvalidArguementError import InvalidArgumentError

from ..dao import AccessTokenDao, RefreshTokenDao

import secrets


class Access:

    secret_key = os.environ["SECRET"]
    access_token_dao = AccessTokenDao()

    @staticmethod
    def get_token():
        """Obtains the Access Token from the Authorization Header
        """
        auth = request.headers.get("Authorization", None)
        if not auth:
            raise AuthError({"code": "authorization_header_missing",
                             "description":
                                 "Authorization header is expected"}, 401)

        parts = auth.split()

        if parts[0].lower() != "bearer":
            raise AuthError({"code": "invalid_header",
                             "description":
                                 "Authorization header must start with"
                                 " Bearer"}, 401)
        elif len(parts) == 1:
            raise AuthError({"code": "invalid_header",
                             "description": "Token not found"}, 401)
        elif len(parts) > 2:
            raise AuthError({"code": "invalid_header",
                             "description":
                                 "Authorization header must be"
                                 " Bearer token"}, 401)

        token = parts[1]
        return token

    @staticmethod
    def generate(user_id):
        """Generates Access Token with the user id and expiration time as payload."""

        payload = {
            'userId': user_id,
            "exp": datetime.utcnow() + timedelta(minutes=15)
        }

        token = jwt.encode(payload, Access.secret_key, algorithm="HS256")

        return token

    @staticmethod
    def decode(token):
        """Decodes the token and returns the user id"""

        payload = jwt.decode(token, Access.secret_key, algorithms=["HS256"])
        user_id = payload["userId"]

        return user_id

    @staticmethod
    def invalidate(token):
        """Invalidates the token by adding it to a blacklist."""
        payload = jwt.decode(token, Access.secret_key, algorithms=["HS256"])
        expires_at = datetime.utcfromtimestamp(payload["exp"])

        # time left to expire is final expiration - current time
        time_left = expires_at - datetime.utcnow()

        return Access.access_token_dao.add(token, time_left)


class Refresh:

    @staticmethod
    def generate(user_id):
        """Generates refresh token"""
        token = secrets.token_hex(nbytes=16)
        # defines expiration to 1 day
        expiration = timedelta(1)

        RefreshTokenDao.add(token, user_id, expiration)

        return token

    @staticmethod
    def verify(token):
        """Verifies if the refresh token was sent and if it is valid."""
        if not token:
            raise InvalidArgumentError({"code": "error", "description": "Refresh token was not sent."}, 400)

        user_id = RefreshTokenDao.search(token)

        if not user_id:
            raise InvalidArgumentError("Refresh token not found", 404)

        return int(user_id)

    @staticmethod
    def invalidate(token):
        """Invalidates the refresh token by removing it from the whitelist."""
        RefreshTokenDao.delete(token)
