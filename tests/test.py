from flask_testing import TestCase
from datetime import datetime
import json

from wsgi import app
from src import db
from src.database.dao import UserDao, DeviceOccupancyDao
from src.controller.DeviceController import DeviceController


class BaseTestCase(TestCase):
    """A base test case."""

    def create_app(self):
        app.config.from_object('config.TestConfig')
        return app

    def setUp(self):

        UserDao.add_user(("test", "test", "test123"))
        UserDao.add_user(("admin", "admin", "admin123"))
        DeviceController(shop_name='test_shop', area=100, ID_user=1).add_device()
        DeviceOccupancyDao.insert_occupancy((1, datetime.now(), 3))

    def tearDown(self):
        meta = db.metadata
        for table in reversed(meta.sorted_tables):
            db.session.execute(table.delete())
        db.session.commit()


class AppTestCase(BaseTestCase):
    def login(self, username, password):
        data = json.dumps({'username': username, 'password': password})
        response = self.client.post('/api/login', data=data, content_type='application/json')
        try:
            token = json.loads(response.data)["authorization"]
        except KeyError:
            token = None

        return response, token

    def test_index(self):
        response = self.client.get('/api/')
        self.assertEqual(404, response.status_code)

    def test_login_auth_correct(self):
        response, _ = self.login('test', 'test123')
        self.assertEqual(200, response.status_code)

        data = response.data
        self.assertIn(b'authorization', data)

    def test_login_auth_username_incorrect(self):
        response, _ = self.login('test' + 'x', 'test123')
        self.assertEqual(404, response.status_code)

    def test_login_auth_password_incorrect(self):
        response, _ = self.login('test', 'test123' + 'x')
        self.assertEqual(400, response.status_code)

    def test_logout(self):
        _, token = self.login('test', 'test123')
        response = self.client.get('/api/logout',
                                   headers={'Authorization': f'Bearer {token}'})
        print(f'Bearer {token}')
        self.assertEqual(200, response.status_code)

    def test_dashboard_protection(self):
        response = self.client.get('/api/dashboard', follow_redirects=True)
        self.assertEqual(401, response.status_code)

    def test_dashboard_content(self):
        _, token = self.login('test', 'test123')
        response = self.client.get('/api/dashboard',
                                   headers={'Authorization': f'Bearer {token}'})
        self.assertIn(b'devices', response.data)

    # def test_create_new_user(self):
    #     self.login('admin', 'admin123')
    #     self.client.get('/edit_area',
    #                     data={'new_name': 'test1', 'new_username': 'test1', 'new_password': 'test1'},
    #                     follow_redirects=True)
    #     response = self.client.get('dashboard')
    #     self.assertIn(b'admin', response.data)

    def test_device_create(self):
        _, token = self.login('test', 'test123')
        data = json.dumps({
                           'deviceID': 1,
                           'shopName': 'test',
                           'area': 100,
                                    })
        response = self.client.post('/api/device/create',
                                    data=data,
                                    content_type='application/json',
                                    headers={'Authorization': f'Bearer {token}'})
        self.assertEqual(200, response.status_code)

    def test_device_edit(self):
        _, token = self.login('test', 'test123')
        data = json.dumps({'deviceID': 1, 'newArea': '200'})

        response = self.client.patch('/api/device/edit',
                                     data=data,
                                     content_type='application/json',
                                     headers={'Authorization': f'Bearer {token}'})
        self.assertEqual(200, response.status_code)

    def test_device_delete(self):
        _, token = self.login('test', 'test123')
        data = json.dumps({'idList': [1]})
        response = self.client.delete('/api/device/delete',
                                      data=data,
                                      content_type='application/json',
                                      headers={'Authorization': f'Bearer {token}'})

        self.assertEqual(200, response.status_code)

    # def test_get_max_people(self):
    #     response = self.client.get('/get_max_people/1')
    #     max_people = response.json['max_people']
    #     self.assertEqual(max_people, 120)
    #
    # def test_add_occupancy(self):
    #     data = {'id': 1, 'occupancy': 5}
    #     response = self.client.post('/add_occupancy',
    #                                 data=json.dumps(data),
    #                                 content_type='application/json')
    #     self.assertEqual(5, response.json["occupancy"])
