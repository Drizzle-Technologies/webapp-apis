import pandas as pd
from datetime import datetime

from ..database.dao import DeviceOccupancyDao


class GraphController:

    def __init__(self, ID_device, n_lines):

        self.ID_device = ID_device
        self.n_lines = n_lines

    @staticmethod
    def sort_by_time(df):

        # Converts timestamp strings to datetime class and sorts the dataframe by timestamp
        df["timestamp"] = df["timestamp"].apply(lambda x: datetime.fromisoformat(x))
        df.sort_values('timestamp', ignore_index=True, inplace=True)

        return df

    @staticmethod
    def format_time_strings(df):

        # Sets a different first label in the x axis
        first_datetime = df.at[0, "timestamp"].strftime("%m/%d/%Y, %H:%M:%S")

        # Converts datetime to string again, but with HOUR:MINUTE:SECONDS format
        df["timestamp"] = df["timestamp"].apply(lambda x: x.strftime("%H:%M"))

        # Creates the x_axis list and sets the first label to a datetime format
        x_axis = df["timestamp"].to_list()
        x_axis[0] = first_datetime

        # Creates the y_axis list
        y_axis = df["occupancy"].to_list()

        return x_axis, y_axis

    def get_graph_data(self):
        """function processes retrieved data from the observations"""

        # Gets dataframe with pandas
        occupancy_sql, bind = DeviceOccupancyDao.retrieve_n_occupancy_observations(self.ID_device)
        occupancy_record = pd.read_sql(occupancy_sql.statement, bind)

        n_lines = self.n_lines or 25

        if not occupancy_record.empty:

            occupancy_record = self.sort_by_time(occupancy_record)

            if n_lines != 100:
                # Truncates dataframe if desired lines are different than 100
                occupancy_record = occupancy_record.tail(n_lines)
                occupancy_record.reset_index(drop=True, inplace=True)

            ax = self.format_time_strings(occupancy_record)

        else:
            ax = ([], [])

        return ax