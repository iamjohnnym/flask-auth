import json
import unittest
from flask import current_app

from service import db
from service.api.models import User
from service.tests.base import BaseTestCase
from service.tests.utils import add_user, get_user_token, login_user, \
    JsonExtendEncoder


class TestAuthBlueprint(BaseTestCase):

    def test_user_registration(self):
        with self.client:
            response = self.client.post(
                '/api/auth/register',
                data=json.dumps({
                    'username': 'testuser',
                    'email': 'test@test.com',
                    'password': '123456'}
                    ),
                content_type='application/json'
                )
            data = json.loads(response.data.decode())
            self.assertTrue(data['auth_token'])
            self.assertTrue(response.content_type == 'application/json')
            self.assertEqual(response.status_code, 201)

    def test_user_registration_duplicate_email(self):
        add_user('test', 'test@test.com', 'test')
        with self.client:
            response = self.client.post(
                '/api/auth/register',
                data=json.dumps({
                    'username': 'test_me',
                    'email': 'test@test.com',
                    'password': 'test'
                    }),
                content_type='application/json',
                )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 409)
            self.assertIn(
                'Email already exists: test@test.com', data['message'])

    def test_user_registration_duplicate_username(self):
        add_user('test', 'test@test.com', 'test')
        with self.client:
            response = self.client.post(
                '/api/auth/register',
                data=json.dumps({
                    'username': 'test',
                    'email': 'test@test.com2',
                    'password': 'test'
                    }),
                content_type='application/json',
                )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 409)
            self.assertIn(
                'Username already exists: test', data['message'])

    def test_user_registration_invalid_json(self):
        with self.client:
            response = self.client.post(
                '/api/auth/register',
                data=json.dumps({}),
                content_type='application/json'
                )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn("Input payload validation failed", data['message'])
            self.assertIn(
                "'username' is a required property",
                data['errors']['username']
                )
            self.assertIn(
                "'email' is a required property",
                data['errors']['email']
                )
            self.assertIn(
                "'password' is a required property",
                data['errors']['password']
                )

    def test_user_registration_invalid_json_keys_no_username(self):
        with self.client:
            response = self.client.post(
                '/api/auth/register',
                data=json.dumps({
                    'email': 'test@test.com',
                    'password': 'test'
                    }),
                content_type='application/json',
                )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn("Input payload validation failed", data['message'])
            self.assertIn(
                "'username' is a required property",
                data['errors']['username']
                )

    def test_user_registration_invalid_json_keys_no_email(self):
        with self.client:
            response = self.client.post(
                '/api/auth/register',
                data=json.dumps({
                    'username': 'testuser',
                    'password': 'test'
                    }),
                content_type='application/json',
                )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn("Input payload validation failed", data['message'])
            self.assertIn(
                "'email' is a required property",
                data['errors']['email']
                )

    def test_user_registration_invalid_json_keys_no_password(self):
        with self.client:
            response = self.client.post(
                '/api/auth/register',
                data=json.dumps({
                    'username': 'testuser',
                    'email': 'test@test.com'
                    }),
                content_type='application/json',
                )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn("Input payload validation failed", data['message'])
            self.assertIn(
                "'password' is a required property",
                data['errors']['password']
                )

    def test_registered_user_login(self):
        with self.client:
            add_user('test', 'test@test.com', 'test')
            response = self.client.post(
                '/api/auth/login',
                data=json.dumps({
                    'email': 'test@test.com',
                    'password': 'test'
                    }),
                content_type='application/json'
                )
            data = json.loads(response.data.decode())
            self.assertIn('test', data['username'])
            self.assertTrue(data['email'])
            self.assertTrue(data['auth_token'])
            self.assertTrue(response.content_type == 'application/json')
            self.assertEqual(response.status_code, 200)

    def test_not_registered_user_login(self):
        with self.client:
            response = self.client.post(
                '/api/auth/login',
                data=json.dumps({
                    'email': 'test@test.com',
                    'password': 'test'
                    }),
                content_type='application/json'
                )
            data = json.loads(response.data.decode())
            self.assertIn(
                'Could not find the requested user',
                data['message']
                )
            self.assertTrue(response.content_type == 'application/json')
            self.assertEqual(response.status_code, 401)

    def test_valid_logout(self):
        add_user('test', 'test@test.com', 'test')
        with self.client:
            # user login
            resp_login = self.client.post(
                '/api/auth/login',
                data=json.dumps({
                    'email': 'test@test.com',
                    'password': 'test'
                    }),
                content_type='application/json'
                )
            # valid token logout
            token = json.loads(resp_login.data.decode())['auth_token']
            response = self.client.get(
                '/api/auth/logout',
                headers={'Authorization': f'Bearer {token}'}
                )
            data = json.loads(response.data.decode())
            self.assertTrue(data['message'] == 'Successfully logged out.')
            self.assertEqual(response.status_code, 200)

    @unittest.skip("Not Implemented")
    def test_invalid_logout_expired_token(self):
        add_user('test', 'test@test.com', 'test')
        current_app.config['JWT_ACCESS_LIFESPAN'] = {'seconds': -1}
        current_app.config['JWT_REFRESH_LIFESPAN'] = {'seconds': -1}
        with self.client:
            resp_login = self.client.post(
                '/api/auth/login',
                data=json.dumps({
                    'email': 'test@test.com',
                    'password': 'test'
                    }),
                content_type='application/json'
                )
            # invalid token logout
            token = json.loads(resp_login.data.decode())['auth_token']
            response = self.client.get(
                '/api/auth/logout',
                headers={'Authorization': f'Bearer {token}'}
                )
            data = json.loads(response.data.decode())
            self.assertEqual(True, data)
            self.assertTrue(
                data['message'] == 'Signature expired. Please log in again.'
                )
            self.assertEqual(response.status_code, 401)

    def test_invalid_logout(self):
        with self.client:
            response = self.client.get(
                '/api/auth/logout',
                headers={'Authorization': 'Bearer invalid'})
            data = json.loads(response.data.decode())
            self.assertTrue(
                data['message'] == 'failed to decode JWT token -- '
                                   'DecodeError: Not enough segments'
                )
            self.assertEqual(response.status_code, 401)

    def test_user_status(self):
        add_user('test', 'test@test.com', 'test')
        with self.client:
            resp_login = self.client.post(
                '/api/auth/login',
                data=json.dumps({
                    'email': 'test@test.com',
                    'password': 'test'
                    }),
                content_type='application/json'
                )
            token = json.loads(resp_login.data.decode())['auth_token']
            response = self.client.get(
                '/api/auth/status',
                headers={'Authorization': f'Bearer {token}'}
                )
            data = json.loads(response.data.decode())
            self.assertTrue(data is not None)
            self.assertTrue(data['username'] == 'test')
            self.assertTrue(data['email'] == 'test@test.com')
            self.assertTrue(data['is_active'] is True)
            self.assertFalse(data['admin'])
            self.assertEqual(response.status_code, 200)

    def test_invalid_status(self):
        with self.client:
            response = self.client.get(
                '/api/auth/status',
                headers={'Authorization': 'Bearer invalid'})
            data = json.loads(response.data.decode())
            self.assertTrue(
                data['message'] == 'failed to decode JWT token -- DecodeError: '
                                   'Not enough segments'
                )
            self.assertEqual(response.status_code, 401)

    @unittest.skip("Not Implemented")
    def test_invalid_logout_inactive(self):
        add_user('test', 'test@test.com', 'test')
        # update user
        with self.client:
            resp_login = self.client.post(
                '/api/auth/login',
                data=json.dumps({
                    'email': 'test@test.com',
                    'password': 'test'
                    }),
                content_type='application/json'
                )
            token = json.loads(resp_login.data.decode())['auth_token']

            user = User.query.filter_by(email='test@test.com').first()
            user.is_active = False
            db.session.commit()

            response = self.client.get(
                '/api/auth/logout',
                headers={'Authorization': f'Bearer {token}'}
                )
            data = json.loads(response.data.decode())
            self.assertIn(
                "The user is not valid or has had access revoked",
                data['message'])
            self.assertEqual(response.status_code, 401)

    def test_invalid_status_inactive(self):
        add_user('test', 'test@test.com', 'test')
        # update user
        user = User.query.filter_by(email='test@test.com').first()
        user.is_active = False
        db.session.commit()
        with self.client:
            resp_login = self.client.post(
                '/api/auth/login',
                data=json.dumps({
                    'email': 'test@test.com',
                    'password': 'test'
                    }),
                content_type='application/json'
                )
            data = json.loads(resp_login.data.decode())
            self.assertIn(
                "The user is not valid or has had access revoked",
                data['message'])
            self.assertEqual(resp_login.status_code, 403)

    def test_refresh_early_refresh_error(self):
        add_user('test', 'test@test.com', 'test')
        with self.client:
            resp_login = self.client.post(
                '/api/auth/login',
                data=json.dumps({
                    'email': 'test@test.com',
                    'password': 'test'
                    }),
                content_type='application/json'
                )
            token = json.loads(resp_login.data.decode())['auth_token']
            response = self.client.get(
                '/api/auth/refresh',
                headers={'Authorization': f'Bearer {token}'}
                )
            data = json.loads(response.data.decode())
            self.assertEqual(401, data['status_code'])
            self.assertEqual('EarlyRefreshError', data['error'])

    def test_disable_user(self):
        add_user('test', 'test@test.com', 'test', 'admin')
        add_user('test2', 'test2@test.com', 'test2')
        with self.client:
            token = get_user_token(self.client, 'test@test.com', 'test')

            response = self.client.patch(
                '/api/auth/disable',
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json',
                data=json.dumps({
                    'email': 'test2@test.com'})
                )

            token2 = login_user(self.client, 'test2@test.com', 'test2')
            data = json.loads(response.data.decode())
            response2 = self.client.get(
                '/api/auth/status',
                headers={'Authorization': f'Bearer {token2}'}
                )
            data = json.loads(response2.data.decode())
            self.assertEqual(401, data['status_code'])
            self.assertEqual('InvalidTokenHeader', data['error'])

    def test_disable_user_no_role(self):
        add_user('test', 'test@test.com', 'test')
        add_user('test2', 'test2@test.com', 'test2')
        with self.client:
            token = get_user_token(self.client, 'test@test.com', 'test')

            response = self.client.patch(
                '/api/auth/disable',
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json',
                data=json.dumps({
                    'email': 'test2@test.com'})
                )
            data = json.loads(response.data.decode())
            self.assertEqual('MissingRoleError', data['error'])
            self.assertEqual(
                "This endpoint requires all the following roles: ['admin']",
                data['message'])
            self.assertEqual(403, data['status_code'])

            token2 = login_user(
                self.client, 'test2@test.com', 'test2')['auth_token']
            response2 = self.client.get(
                '/api/auth/status',
                headers={'Authorization': f'Bearer {token2}'}
                )
            data = json.loads(response2.data.decode())
            self.assertEqual(200, response2.status_code)
            self.assertTrue(data['email'])
            self.assertTrue(data['username'])
            self.assertTrue(data['is_active'])


if __name__ == '__main__':
    unittest.main()
