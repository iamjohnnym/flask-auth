import json
import unittest

from service import db
from service.api.models import User
from service.tests.base import BaseTestCase
from service.tests.utils import add_user, get_user_token, get_url_with_token


class TestUserService(BaseTestCase):
    """Tests for the Users Service."""

    def test_users(self):
        """Ensure the /ping route behaves correctly."""
        response = self.client.get('/api/users/ping')
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertIn('pong!', data['message'])
        self.assertIn('success', data['status'])

    def test_add_user(self):
        """Ensure a new user can be added to the database."""
        add_user('test', 'test@test.com', 'test')
        # update user
        user = User.query.filter_by(email='test@test.com').first()
        user.admin = True
        db.session.commit()
        with self.client:
            token = get_user_token(self.client, 'test@test.com', 'test')
            response = self.client.post(
                '/api/users/',
                data=json.dumps({
                    'username': 'test_me',
                    'email': 'test_me@example.com',
                    'password': 'Downf0ryourRIGHTtoParty!',
                    }),
                content_type='application/json',
                headers={'Authorization': f'Bearer {token}'}
                )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 201)
            self.assertIn('test_me@example.com', data['email'])
            self.assertNotIn('password', data)

    def test_add_user_invalid_json(self):
        """Ensure error is thrown if the JSON object is empty."""
        add_user('test', 'test@test.com', 'test')
        # update user
        user = User.query.filter_by(email='test@test.com').first()
        user.admin = True
        db.session.commit()
        with self.client:
            token = get_user_token(self.client, 'test@test.com', 'test')
            response = self.client.post(
                '/api/users/',
                data=json.dumps({}),
                content_type='application/json',
                headers={'Authorization': f'Bearer {token}'}
                )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn("Input payload validation failed", data['message'])
            self.assertIn(
                "'email' is a required property", data['errors']['email']
                )
            self.assertIn(
                "'username' is a required property", data['errors']['username']
                )
            self.assertIn(
                "'password' is a required property", data['errors']['password']
                )

    def test_add_user_invalid_json_keys(self):
        """
        Ensure error is thrown if the JSON object does not have a username key.
        """
        add_user('test', 'test@test.com', 'test')
        # update user
        user = User.query.filter_by(email='test@test.com').first()
        user.admin = True
        db.session.commit()
        with self.client:
            token = get_user_token(self.client, 'test@test.com', 'test')
            response = self.client.post(
                '/api/users/',
                data=json.dumps({
                    'email': 'test_me@example.com',
                    'password': 'Downf0ryourRIGHTtoParty!',
                    }),
                content_type='application/json',
                headers={'Authorization': f'Bearer {token}'}
                )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn("Input payload validation failed", data['message'])
            self.assertIn(
                "'username' is a required property", data['errors']['username']
                )

    def test_add_user_duplicate_username(self):
        """Ensure error is thrown if the email already exists."""
        add_user('test', 'test@test.com', 'test')
        # update user
        user = User.query.filter_by(email='test@test.com').first()
        user.admin = True
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
            token = json.loads(resp_login.data.decode())['auth_token']
            self.client.post(
                '/api/users/',
                data=json.dumps({
                    'username': 'test_me',
                    'email': 'test_me@example.com',
                    'password': 'Downf0ryourRIGHTtoParty!',
                    }),
                content_type='application/json',
                headers={'Authorization': f'Bearer {token}'}
                )
            token_two = json.loads(resp_login.data.decode())['auth_token']
            response = self.client.post(
                '/api/users/',
                data=json.dumps({
                    'username': 'test_me',
                    'email': 'test_me2@example.com',
                    'password': 'Downf0ryourRIGHTtoParty!',
                    }),
                content_type='application/json',
                headers={'Authorization': f'Bearer {token_two}'}
                )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 409)
            self.assertIn(
                'Username already in use: test_me', data['message']
                )

    def test_add_user_duplicate_email(self):
        """Ensure error is thrown if the email already exists."""
        user = add_user('test', 'test@test.com', 'test')
        user.admin = True
        db.session.commit()
        with self.client:
            token = get_user_token(
                self.client, 'test@test.com', 'test'
                )

            self.client.post(
                '/api/users/',
                data=json.dumps({
                    'username': 'test_me',
                    'email': 'test_me@example.com',
                    'password': 'Downf0ryourRIGHTtoParty!',
                    }),
                content_type='application/json',
                headers={'Authorization': f'Bearer {token}'}
                )
            token_two = get_user_token(
                self.client, 'test@test.com', 'test'
                )
            response = self.client.post(
                '/api/users/',
                data=json.dumps({
                    'username': 'test_me',
                    'email': 'test_me@example.com',
                    'password': 'Downf0ryourRIGHTtoParty!',
                    }),
                content_type='application/json',
                headers={'Authorization': f'Bearer {token_two}'}
                )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 409)
            self.assertIn(
                'Email already in use: test_me@example.com', data['message']
                )

    def test_single_user(self):
        """Ensure get single user behaves correctly."""
        user = add_user(
            'test_me', 'test_me@example.com', 'Downf0ryourRIGHTtoParty!'
            )
        with self.client:
            token = get_user_token(
                self.client, 'test_me@example.com', 'Downf0ryourRIGHTtoParty!'
                )
            response = self.client.get(
                f'/api/users/{user.id}',
                content_type='application/json',
                headers={'Authorization': f'Bearer {token}'}
                )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertIn('test_me', data['username'])
            self.assertIn('test_me@example.com', data['email'])

    def test_single_user_no_id(self):
        """Ensure error is thrown if an id is not found."""
        add_user(
            'test_me', 'test_me@example.com', 'Downf0ryourRIGHTtoParty!'
            )
        with self.client:
            token = get_user_token(
                self.client, 'test_me@example.com', 'Downf0ryourRIGHTtoParty!'
                )
            response = self.client.get(
                f'/api/users/blah',
                content_type='application/json',
                headers={'Authorization': f'Bearer {token}'}
                )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertIn('User Not Found by Id blah', data['message'])

    def test_single_user_incorrect_id(self):
        """Ensure error is thrown if the id does not exist."""
        add_user(
            'test_me', 'test_me@example.com', 'Downf0ryourRIGHTtoParty!'
            )
        with self.client:
            token = get_user_token(
                self.client, 'test_me@example.com', 'Downf0ryourRIGHTtoParty!'
                )
            response = self.client.get(
                f'/api/users/999',
                content_type='application/json',
                headers={'Authorization': f'Bearer {token}'}
                )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertIn('User Not Found by Id 999', data['message'])

    def test_single_user_no_auth(self):
        """Ensure get single user behaves correctly."""
        user = add_user(
            'test_me', 'test_me@example.com', 'Downf0ryourRIGHTtoParty!'
            )
        with self.client:
            response = self.client.get(f'/api/users/{user.id}')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 401)
            self.assertIn(
                "JWT token not found in headers under 'Authorization'",
                data['message']
                )

    def test_single_user_no_id_no_auth(self):
        """Ensure error is thrown if an id is not found."""
        with self.client:
            response = self.client.get('/api/users/blah')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 401)
            self.assertIn(
                "JWT token not found in headers under 'Authorization'",
                data['message']
                )

    def test_single_user_incorrect_id_no_auth(self):
        """Ensure error is thrown if the id does not exist."""
        with self.client:
            response = self.client.get('/api/users/999')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 401)
            self.assertIn(
                "JWT token not found in headers under 'Authorization'",
                data['message']
                )

    def test_all_users(self):
        """Ensure get all users behaves correctly."""
        add_user('test_me', 'test_me@example.com', 'Downf0ryourRIGHTtoParty!')
        add_user(
            'fletcher', 'fletcher@notreal.com', 'Downf0ryourRIGHTtoParty!'
            )
        with self.client:
            token = get_user_token(
                self.client, 'test_me@example.com', 'Downf0ryourRIGHTtoParty!'
                )
            response = get_url_with_token(self.client, '/api/users/', token)

            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(data), 2)
            self.assertIn('test_me', data[0]['username'])
            self.assertIn(
                'test_me@example.com', data[0]['email']
                )
            self.assertTrue(data[0]['is_active'])
            self.assertFalse(data[0]['admin'])
            self.assertIn('fletcher', data[1]['username'])
            self.assertIn(
                'fletcher@notreal.com', data[1]['email']
                )
            self.assertTrue(data[1]['is_active'])
            self.assertFalse(data[1]['admin'])

    def test_add_user_invalid_json_keys_no_password(self):
        """
        Ensure error is thrown if the JSON object
        does not have a password key.
        """
        add_user('test', 'test@test.com', 'test')
        # update user
        user = User.query.filter_by(email='test@test.com').first()
        user.admin = True
        db.session.commit()
        with self.client:
            token = get_user_token(self.client, 'test@test.com', 'test')
            response = self.client.post(
                '/api/users/',
                data=json.dumps({
                    'username': 'test_me',
                    'email': 'test_me@sonotreal.com'
                    }),
                content_type='application/json',
                headers={'Authorization': f'Bearer {token}'}
                )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn("Input payload validation failed", data['message'])
            self.assertIn(
                "'password' is a required property", data['errors']['password']
                )

    @unittest.skip("Not Implemented")
    def test_add_user_inactive(self):
        add_user('test', 'test@test.com', 'test')
        # update user
        user = User.query.filter_by(email='test@test.com').first()
        user.is_active = False
        db.session.commit()
        with self.client:
            token = get_user_token(self.client, 'test@test.com', 'test')
            response = self.client.post(
                '/api/users/',
                data=json.dumps({
                    'username': 'test_me',
                    'email': 'test_me@sonotreal.com',
                    'password': 'test'
                    }),
                content_type='application/json',
                headers={'Authorization': f'Bearer {token}'}
                )
            data = json.loads(response.data.decode())
            self.assertTrue(data == 'Provide a valid auth token.')
            self.assertEqual(response.status_code, 401)

    @unittest.skip("Not Implemented")
    def test_add_user_not_admin(self):
        add_user('test', 'test@test.com', 'test')
        with self.client:
            # user login
            token = get_user_token(self.client, 'test@test.com', 'test')
            response = self.client.post(
                '/api/users/',
                data=json.dumps({
                    'username': 'test_me',
                    'email': 'test_me@sonotreal.com',
                    'password': 'test'
                    }),
                content_type='application/json',
                headers={'Authorization': f'Bearer {token}'}
                )
            data = json.loads(response.data.decode())
            self.assertTrue(
                data == 'You do not have permission to do that.'
                )
            self.assertEqual(response.status_code, 401)


if __name__ == '__main__':
    unittest.main()
