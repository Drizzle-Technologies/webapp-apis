from ..database.database import db, DevicesOccupancy

import secrets


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

    # @staticmethod
    # def update_current_occupancy(values):
    #     """Updates the current occupancy in the Devices table"""
    #
    #     ID, current_occupancy = values
    #
    #     device = Device.query.filter_by(ID=ID).first()
    #     device.current_occupancy = current_occupancy
    #
    #     db.session.commit()
