import unittest

from sqlalchemy.exc import IntegrityError

from service import db
from service.api.models import User
from service.tests.base import BaseTestCase
from service.tests.utils import add_user


class TestUserModel(BaseTestCase):

    def test_add_user(self):
        user = add_user('testuser', 'test@test.com', 'test')
        self.assertTrue(user.id)
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@test.com')
        self.assertTrue(user.is_active)
        self.assertTrue(user.password)
        self.assertFalse(user.admin)

    def test_add_user_duplicate_username(self):
        add_user('testuser', 'test@test.com', 'Downf0ryourRIGHTtoParty!')
        duplicate_user = User(
            username='testuser',
            email='test@test2.com',
            password='Downf0ryourRIGHTtoParty!',
            )
        db.session.add(duplicate_user)
        self.assertRaises(IntegrityError, db.session.commit)

    def test_add_user_duplicate_email(self):
        add_user('testuser', 'test@test.com', 'Downf0ryourRIGHTtoParty!')
        duplicate_user = User(
            username='testuser2',
            email='test@test.com',
            password='Downf0ryourRIGHTtoParty!',
            )
        db.session.add(duplicate_user)
        self.assertRaises(IntegrityError, db.session.commit)

    def test_to_json(self):
        user = add_user(
            'testuser', 'test@test.com', 'Downf0ryourRIGHTtoParty!'
            )
        self.assertTrue(isinstance(user.to_json(), dict))

    def test_passwords_are_random(self):
        user_one = add_user(
            'testuser', 'test@test.com', 'Downf0ryourRIGHTtoParty!'
            )
        user_two = add_user(
            'testuser2', 'test@test2.com', 'Downf0ryourRIGHTtoParty!'
            )
        self.assertNotEqual(user_one.password, user_two.password)


if __name__ == '__main__':
    unittest.main()
