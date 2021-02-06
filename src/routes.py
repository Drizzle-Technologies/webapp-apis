from flask import render_template, request, redirect, url_for, flash, session, jsonify, Blueprint
from flask import current_app as app

from datetime import datetime, timedelta
import pytz

import jwt

from .database.dao import UserDao, DeviceDao, DeviceOccupancyDao, TokenDao

from .helper.helper import calculate_max_people, is_not_logged_in, verify_user, verify_password

from .helper.auth import requires_auth


secret_key = app.config["SECRET_KEY"]
api = Blueprint('api', __name__)

user_dao = UserDao()
devices_dao = DeviceDao()
devices_occupancy_dao = DeviceOccupancyDao()
token_dao = TokenDao()

# This is how Flask routes work. The app.route decorator sets a route to our site. For example: imagine our app is
# google.com. We can add a route "/images" (google.com/images) to create a new page for image search.


@api.route('/login', methods=["POST"])
def login():
    """Route used for login authentication. Front-end sends username and password and
    if they are correct, the api returns a JSON Web Token."""
    login_data = request.get_json()
    username = login_data["username"]
    password = login_data["password"]

    user = user_dao.search_by_username(username)

    # If user or password are incorrect, raises InvalidArgumentError, which is treated in errors.handlers.py
    verify_user(user)
    verify_password(user, password)

    payload = {
        'userId': user.ID,
        "exp": datetime.utcnow() + timedelta(minutes=15)
    }

    token = jwt.encode(payload, secret_key, algorithm="HS256")
    res = {
            'authorization': token,
            'timestamp': datetime.now(pytz.timezone("America/Sao_Paulo")).isoformat()
    }

    return jsonify(res), 200


@api.route('/logout')
@requires_auth
def logout():
    req = request.headers.get("Authorization", None)
    token = req.split()[1]

    token_dao.add_to_blacklist(token)
    res = {
        'code': 'success',
        'description': 'logout successful'
    }
    return jsonify(res), 200


@api.route('/dashboard')
@requires_auth
def dashboard():
    """Route returns data about the user's dashboard."""
    req = request.headers.get("Authorization", None)

    token = req.split()[1]
    payload = jwt.decode(token, secret_key, algorithms=["HS256"])

    # Gets user's devices list to display on table
    devices = devices_dao.get_user_devices(payload["userId"])

    res = {'devices': devices}
    return jsonify(res), 200


# @app.route('/create_user', methods=['POST'])
# def create_user():
#     """This route creates a new user."""
#
#     # Gets name, username, and password assigned to new user
#     name = request.form['new_name']
#     username = request.form['new_username']
#     password = request.form['new_password']
#
#     values = (name, username, password)
#
#     success = user_dao.add_user(values)
#
#     # Flashes success message
#     if success:
#         flash("Usuário foi criado.", "alert-success")
#
#     return redirect(url_for('dashboard'))
#
#
# @app.route('/save_device', methods=["POST"])
# def save_device():
#     """This route is used to save new devices on the database. It cannot be directly accessed."""
#
#     # Each form input is saved in a different variable.
#     ID_user = session["logged_in"]
#     shop_name = request.form['shop_name']
#     area = int(request.form['area'])
#     max_people = calculate_max_people(area)
#
#     # We then form a tuple, which is roughly an immutable vector.
#     new_device = (ID_user, shop_name, area, max_people)
#
#     # Finally we add the device to the database
#     device_added = devices_dao.add_device(new_device)
#     if device_added:
#         flash("O dispositivo foi adicionado!", "alert-success")
#
#     # And we are redirected to our index page.
#     return redirect(url_for('dashboard'))
#
#
# @app.route('/edit_area', methods=["POST"])
# def edit_area():
#     """This route is used to edit a device's area"""
#
#     # Get device's ID and new area
#     ID = int(request.form["device_ID_editArea"])
#     new_area = int(request.form["new_area"])
#
#     update_success = devices_dao.update_area(ID, new_area)
#
#     if update_success:
#         flash("O valor da área foi atualizado.", "alert-success")
#
#     return redirect(url_for('dashboard'))
#
#
# @app.route('/delete', methods=["POST"])
# def delete():
#     """This route is used to delete a device"""
#
#     # Gets device's ID
#     ID = request.form['device_ID_delete']
#
#     device_deleted = devices_dao.delete_device(ID)
#     if device_deleted:
#         flash("O dispositivo foi deletado", "alert-danger")
#
#     return redirect(url_for('dashboard'))
#
#
# @app.route('/get_max_people/<ID>')
# def get_max_people(ID):
#     """This route is used as an API to the devices information. A GET request is done in this URL, such as
#     localhost/controladores/1) and it retrieves the maximum capacity of the building."""
#
#     # Gets device's max number of people
#     max_people = devices_dao.retrieve_max_people(ID).max_people
#     max_dict = {'max_people': max_people}
#
#     # Transforms dictionary into json and sends it
#     return jsonify(max_dict)
#
#
# @app.route('/add_occupancy', methods=["POST"])
# def add_occupancy():
#     """This route adds a new occupancy record to the DeviceOccupancy table and updates current_occupancy in the Device
#     table."""
#
#     # Gets the json
#     occupancy_json = request.get_json()
#
#     # Accesses each of the information provided
#     ID_device = occupancy_json['id']
#     occupancy = occupancy_json['occupancy']
#     timestamp = datetime.now(pytz.timezone("America/Sao_Paulo")).isoformat()
#
#     # Inserts values in DeviceOccupancy and updates Device's current_occupancy column
#     insert_values = (ID_device, timestamp, occupancy)
#     update_values = (ID_device, occupancy)
#
#     devices_occupancy_dao.insert_occupancy(insert_values)
#     devices_occupancy_dao.update_current_occupancy(update_values)
#
#     # Returns the json to confirm the success
#     return jsonify(occupancy_json)
