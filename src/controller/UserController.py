from werkzeug.security import check_password_hash

from ..errors.InvalidArguementError import InvalidArgumentError


class UserController:

    @staticmethod
    def verify_user(user):
        if not user:
            raise InvalidArgumentError({"code": "InvalidArgumentError",
                                        "description": "This user does not exist."}, 404)

    @staticmethod
    def verify_password(user, password):
        """Method validates a password by comparing the stored hash to the input password."""
        if not check_password_hash(user.password, password):
            raise InvalidArgumentError({"code": "InvalidArgumentError",
                                        "description": "Password incorrect."}, 400)