import pandas as pd
from datetime import datetime

from ..dao import DeviceOccupancyDao


class GraphController:

    def __init__(self, ID_device, n_lines):

        self.ID_device = ID_device
        self.n_lines = n_lines

    @staticmethod
    def sort_by_time(df):

        # Converts timestamp strings to datetime class and sorts the dataframe by timestamp
        df["sort"] = df["timestamp"].apply(lambda x: datetime.fromisoformat(x))
        df.sort_values('sort', ignore_index=True, inplace=True)
        df.drop(["sort"], axis=1, inplace=True)

        return df

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

            # Sets a different first label in the x axis
            first_datetime = occupancy_record.at[0, "timestamp"]

            # Creates the x_axis list and sets the first label to a datetime format
            x_axis = occupancy_record["timestamp"].to_list()

            # Creates the y_axis list
            y_axis = occupancy_record["occupancy"].to_list()

            ax = (x_axis, y_axis, first_datetime)

        else:
            ax = ([], [])

        return ax