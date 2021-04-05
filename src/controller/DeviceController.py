from ..dao import DeviceDao


class DeviceController:

    def __init__(self, ID=None, shop_name="", area=None, ID_user=None):
        self._ID = ID
        self._shop_name = shop_name
        self._area = area
        self._ID_user = ID_user


    @staticmethod
    def calculate_max_people(area):
        """Calculates the max number of people allowed in a building"""
        standard_capacity = area * 2

        # This numbers are defined for the 4th level of flexibilization of São Paulo state quarantine
        pandemic_capacity = standard_capacity * 0.6
        return int(pandemic_capacity)

    def add_device(self):

        max_people = self.calculate_max_people(self._area)
        DeviceDao.add_device(self._ID_user, self._shop_name, self._area, max_people)

    def update_area(self):

        max_people = self.calculate_max_people(self._area)
        DeviceDao.update_area(self._ID, self._area, max_people)
