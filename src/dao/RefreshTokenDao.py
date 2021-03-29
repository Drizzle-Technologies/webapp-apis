from ..database.whitelist import whitelist


class RefreshTokenDao:

    @staticmethod
    def add(token, user_id, expiration):
        whitelist.set(token, user_id, ex=expiration)

        return token

    @staticmethod
    def search(token):
        return whitelist.get(token)

    @staticmethod
    def delete(token):
        whitelist.delete(token)