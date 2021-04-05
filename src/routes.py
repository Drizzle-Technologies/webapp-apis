from flask import request, jsonify, Blueprint
from flask import current_app as app

import jwt

from .dao import UserDao, DeviceDao

from .controller.UserController import UserController
from .controller.DeviceController import DeviceController
from .controller.GraphController import GraphController


from .auth.auth import bearer, refresh
from .auth.tokens import Access, Refresh


secret_key = app.config["SECRET_KEY"]
api = Blueprint('api', __name__)

user_dao = UserDao()
devices_dao = DeviceDao()


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
    UserController.verify_user(user)
    UserController.verify_password(user, password)

    access_token = Access.generate(user.ID)
    refresh_token = Refresh.generate(user.ID)

    res = {
        'authorization': access_token,
        'refreshToken': refresh_token,
    }

    return jsonify(res), 200


@api.route('/refresh', methods=["POST"])
def update_token():
    """Route used to refresh the Access Token"""
    req = request.get_json()
    token = req["refreshToken"]

    refresh_token, access_token = refresh(token)

    res = {
        "accessToken": access_token,
        "refreshToken": refresh_token
    }

    return jsonify(res), 200


@bearer
@api.route('/logout', methods=["POST"])
def logout():
    access_token = Access.get_token()

    req = request.get_json()
    refresh_token = req["refreshToken"]

    Access.invalidate(access_token)
    Refresh.invalidate(refresh_token)

    res = {
        'code': 'success',
        'description': 'logout successful'
    }
    return jsonify(res), 200


@api.route('/user/devices')
@bearer
def user_devices():
    """Route returns data about the user's dashboard."""
    token = Access.get_token()

    user_id = Access.decode(token)

    # Gets user's devices list to display on table
    devices = devices_dao.get_user_devices(user_id)

    res = {'devices': devices}
    return jsonify(res), 200


@api.route('/user', methods=["GET"])
@bearer
def user_general():
    """Route returns the name and username through the token"""
    token = Access.get_token()
    user_id = Access.decode(token)

    user = user_dao.search_by_id(user_id)

    res = {
        'name': user.name,
        'username': user.username
    }

    return jsonify(res), 200


@api.route('/device/create', methods=["POST"])
@bearer
def device_create():
    """Route for a user to create a new device."""
    token = Access.get_token()

    device_data = request.get_json()
    shop_name = device_data["shopName"]
    area = float(device_data["area"])

    payload = jwt.decode(token, secret_key, algorithms=["HS256"])
    user_ID = payload["userId"]

    DeviceController(shop_name=shop_name, area=area, ID_user=user_ID).add_device()

    res = {
        'code': 'success',
        'description': 'new device created'
    }

    return jsonify(res), 200


@api.route('device/edit', methods=["PATCH"])
@bearer
def device_edit():
    """Route for a user to edit a device values."""
    device_data = request.get_json()
    ID_device = device_data["deviceID"]
    new_area = int(device_data["newArea"])

    DeviceController(ID_device, area=new_area).update_area()

    res = {
        'code': 'success',
        'description': 'device edited'
    }

    return jsonify(res), 200


@api.route('device/delete', methods=["DELETE"])
@bearer
def device_delete():
    """Route for a user to delete a device's list."""
    device_data = request.get_json()
    ID_list = device_data["idList"]

    for ID in ID_list:
        devices_dao.delete_device(ID)

    res = {
        'code': 'success',
        'description': 'device deleted'
    }

    return jsonify(res), 200


@api.route('occupancy/graph/<ID_device>/<n_lines>', methods=["GET"])
@bearer
def occupancy_graph(ID_device, n_lines):
    """Route to use the occupancy's graph"""
    graph_controller = GraphController(int(ID_device), int(n_lines))
    x_axis, y_axis, first_datetime = graph_controller.get_graph_data()

    res = {
        'graph': {
             'labels': x_axis,
             'datasets': [{'label': 'Histórico de ocupação', 'data': y_axis}]
        },
        'firstDatetime': first_datetime
    }

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
