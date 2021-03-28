from .database import db, Device, User, DevicesOccupancy
from .blacklist import red
from werkzeug.security import generate_password_hash
import hashlib
import secrets
import jwt


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


class DeviceDao:

    @staticmethod
    def add_device(ID_user, shop_name, area, max_people):
        """Method adds a new device to the Device table"""

        ids = [device_id.ID for device_id in Device.query.all()]
        if not ids:
            ids = [0]
        ids.sort()
        last_id = ids[-1]

        device = Device(ID=last_id+1, ID_user=ID_user, shop_name=shop_name, area=area, max_people=max_people)
        db.session.add(device)
        db.session.commit()

        return True

    @staticmethod
    def delete_device(ID):
        """Method deletes device from the Device table by searching by id"""

        device = Device.query.filter_by(ID=ID).first()
        db.session.delete(device)
        db.session.commit()
        return True

    @staticmethod
    def get_ID_devices():
        """Gets the ids from all the devices"""

        return Device.query.with_entities(Device.ID).distinct(), db.session.bind

    @staticmethod
    def get_user_devices(ID_user):
        """Gets the devices from a specific user through the user's id"""
        obj_devices = Device.query.filter_by(ID_user=ID_user).order_by(Device.ID).all()

        dict_devices = [device.__dict__ for device in obj_devices]

        for i, device in enumerate(dict_devices):
            # Deletes extra attribute we don't use
            device.pop('_sa_instance_state')
            device.pop('ID_user')

            # Iterates over the device keys and return them lower case
            dict_devices[i] = {k.lower(): v for k, v in device.items()}

        return dict_devices

    @staticmethod
    def retrieve_max_people(ID):
        """Retrieves the max number of people allowed in a device's building by searching by ID."""

        return Device.query.filter_by(ID=ID).first()

    @staticmethod
    def update_area(ID, new_area, new_max_people):
        """Updates the area and max_people through the device's ID in the Device table"""

        device = Device.query.filter_by(ID=ID).first()
        device.area = new_area

        # updating area implicates updating max_people
        device.max_people = new_max_people

        db.session.commit()


class DeviceOccupancyDao:

    @staticmethod
    def insert_occupancy(values):
        """Inserts a new occupancy record in DevicesOccupancy"""

        ID = secrets.token_hex(nbytes=16)
        ID_device, timestamp, occupancy = values

        devices_occupancy = DevicesOccupancy(ID=ID, ID_device=ID_device, timestamp=timestamp, occupancy=occupancy)

        db.session.add(devices_occupancy)
        db.session.commit()

    @staticmethod
    def retrieve_n_occupancy_observations(ID_device):
        """Retrieves 100 rows of occupancy observations from DevicesOccupancy"""

        return DevicesOccupancy.query.filter_by(ID_device=ID_device).order_by(DevicesOccupancy.timestamp.desc()).limit(100),\
               db.session.bind

    @staticmethod
    def update_current_occupancy(values):
        """Updates the current occupancy in the Devices table"""

        ID, current_occupancy = values

        device = Device.query.filter_by(ID=ID).first()
        device.current_occupancy = current_occupancy

        db.session.commit()


class TokenDao:

    @staticmethod
    def generate_hash_token(token):
        sha = hashlib.sha256()
        sha.update(token.encode('ascii'))
        token_hash = sha.hexdigest()

        return token_hash

    def add_to_blacklist(self, token):

        token_hash = self.generate_hash_token(token)
        red.set(token_hash, "")

        return True

    def search_in_blacklist(self, token):
        token_hash = self.generate_hash_token(token)
        res = red.exists(token_hash)

        if res:
            raise jwt.InvalidTokenError

        return True