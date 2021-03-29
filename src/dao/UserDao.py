from ..database.database import db, User

from werkzeug.security import generate_password_hash


class UserDao:

    @staticmethod
    def search_by_username(username):
        """Method seacrches a user by his or her username."""

        return User.query.filter_by(username=username).first()

    @staticmethod
    def add_user(values):
        """Method adds a new user to the User table."""

        name, username, password = values

        password_hash = generate_password_hash(password)

        ids = [users.ID for users in User.query.all()]
        if not ids:
            ids = [0]
        ids.sort()
        last_id = ids[-1]

        user = User(ID=last_id+1, name=name, username=username, password=password_hash)
        db.session.add(user)
        db.session.commit()

        return True

    def search_by_id(self, ID):
        """Method searches the username through the ID"""

        return User.query.filter_by(ID=ID).first()

