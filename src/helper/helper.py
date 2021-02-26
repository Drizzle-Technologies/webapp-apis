from ..errors.InvalidArguementError import InvalidArgumentError
from ..database.dao import DeviceOccupancyDao

from flask import request
import pandas as pd
from datetime import datetime
from werkzeug.security import check_password_hash


def calculate_max_people(area):
    """Calculates the max number of people allowed in a building"""
    stadard_capacity = area*2

    # This numbers are defined for the 4th level of flexibilization of São Paulo state quarantine
    pandemic_capacity = stadard_capacity * 0.6
    return int(pandemic_capacity)


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

    occupancy_sql, bind = DeviceOccupancyDao.retrieve_n_occupancy_observations(ID_device)
    occupancy_record = pd.read_sql(occupancy_sql.statement, bind)

    n_lines = n_lines or 25

    if not occupancy_record.empty:

        occupancy_record["timestamp"] = occupancy_record["timestamp"].apply(lambda x: datetime.fromisoformat(x))
        occupancy_record.sort_values('timestamp', ignore_index=True, inplace=True)

        if n_lines != 100:
            occupancy_record = occupancy_record.tail(n_lines)

    x_axis = occupancy_record["timestamp"].to_list()
    y_axis = occupancy_record["occupancy"].to_list()

    return x_axis, y_axis


def is_not_logged_in(session):
    """Returns whether the user is logged in or not"""
    return 'logged_in' not in session or session['logged_in'] is None
