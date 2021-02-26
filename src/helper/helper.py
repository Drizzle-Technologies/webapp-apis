from ..errors.InvalidArguementError import InvalidArgumentError
from ..database.dao import DeviceOccupancyDao

from flask import request
import pandas as pd
from datetime import datetime
from werkzeug.security import check_password_hash


def verify_user(user):
    if not user:
        raise InvalidArgumentError({"code": "InvalidArgumentError",
                                    "description": "This user does not exist."}, 404)


def verify_password(user, password):
    """Method validates a password by comparing the stored hash to the input password."""
    if not check_password_hash(user.password, password):
        raise InvalidArgumentError({"code": "InvalidArgumentError",
                                    "description": "Password incorrect."}, 400)


def get_token():
    req = request.headers.get("Authorization", None)
    token = req.split()[1]

    return token


def get_graph_data(ID_device, n_lines):
    """function processes retrieved data from the observations"""

    # Gets dataframe with pandas
    occupancy_sql, bind = DeviceOccupancyDao.retrieve_n_occupancy_observations(ID_device)
    occupancy_record = pd.read_sql(occupancy_sql.statement, bind)

    n_lines = n_lines or 25

    if not occupancy_record.empty:

        if n_lines != 100:
            # Truncates dataframe if desired lines are different than 100
            occupancy_record = occupancy_record.tail(n_lines)

        # Converts timestamp strings to datetime class and sorts the dataframe by timestamp
        occupancy_record["timestamp"] = occupancy_record["timestamp"].apply(lambda x: datetime.fromisoformat(x))
        occupancy_record.sort_values('timestamp', ignore_index=True, inplace=True)

        # Sets a different first label in the x axis
        first_datetime = occupancy_record.at[0, "timestamp"].strftime("%m/%d/%Y, %H:%M:%S")

        # Converts datetime to string again, but with HOUR:MINUTE:SECONDS format
        occupancy_record["timestamp"] = occupancy_record["timestamp"].apply(lambda x: x.strftime("%H:%M:%S"))

        # Creates the x_axis list and sets the first label to a datetime format
        x_axis = occupancy_record["timestamp"].to_list()
        x_axis[0] = first_datetime

        # Creates the y_axis list
        y_axis = occupancy_record["occupancy"].to_list()

        ax = (x_axis, y_axis)

    else:
        ax = ([], [])

    return ax


def is_not_logged_in(session):
    """Returns whether the user is logged in or not"""
    return 'logged_in' not in session or session['logged_in'] is None
