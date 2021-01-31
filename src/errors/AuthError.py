class AuthError(Exception):
    def __init__(self, error, status):
        self.error = error
        self.status = status

    def __str__(self):
        return self.error
