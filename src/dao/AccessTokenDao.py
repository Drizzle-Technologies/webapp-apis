from ..database.blacklist import blacklist

import hashlib

import jwt


class AccessTokenDao:

    @staticmethod
    def generate_hash_token(token):
        sha = hashlib.sha256()
        sha.update(token.encode('ascii'))
        token_hash = sha.hexdigest()

        return token_hash

    def add(self, token, expiration):

        token_hash = self.generate_hash_token(token)
        blacklist.set(token_hash, "", ex=expiration)

        return True

    def search(self, token):
        token_hash = self.generate_hash_token(token)
        res = blacklist.exists(token_hash)

        if res:
            raise jwt.InvalidTokenError

        return False
