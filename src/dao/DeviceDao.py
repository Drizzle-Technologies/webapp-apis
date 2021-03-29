from ..database.database import db, Device


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
