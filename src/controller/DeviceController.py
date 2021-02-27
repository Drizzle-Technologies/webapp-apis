class DeviceController:

    @staticmethod
    def calculate_max_people(area):
        """Calculates the max number of people allowed in a building"""
        standard_capacity = area * 2

        # This numbers are defined for the 4th level of flexibilization of São Paulo state quarantine
        pandemic_capacity = standard_capacity * 0.6
        return int(pandemic_capacity)