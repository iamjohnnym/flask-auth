import os
import unittest
from flask import current_app
from flask_testing import TestCase
from service import create_app

app = create_app()


class TestDevelopmentConfig(TestCase):
    def create_app(self):
        app.config.from_object('service.config.DevelopmentConfig')
        return app

    def test_app_is_development(self):
        self.assertEqual(
            app.config['SECRET_KEY'], os.environ.get('SECRET_KEY')
            )
        self.assertFalse(current_app is None)
        self.assertEqual(
            app.config['SQLALCHEMY_DATABASE_URI'],
            os.environ.get('DATABASE_URL')
            )
        self.assertTrue(app.config['DEBUG_TB_ENABLED'])


class TestTestingConfig(TestCase):
    def create_app(self):
        app.config.from_object('service.config.TestingConfig')
        return app

    def test_app_is_testing(self):
        self.assertEqual(
            app.config['SECRET_KEY'], "testing-and-thats-it"
            )
        self.assertTrue(app.config['TESTING'])
        self.assertFalse(app.config['PRESERVE_CONTEXT_ON_EXCEPTION'])
        self.assertEqual(
            app.config['SQLALCHEMY_DATABASE_URI'],
            "sqlite:///:memory:"
            )
        self.assertFalse(app.config['DEBUG_TB_ENABLED'])


class TestProductionConfig(TestCase):
    def create_app(self):
        app.config.from_object('service.config.ProductionConfig')
        return app

    def test_app_is_production(self):
        self.assertEqual(
            app.config['SECRET_KEY'], os.environ.get('SECRET_KEY')
            )
        self.assertFalse(app.config['TESTING'])
        self.assertFalse(app.config['DEBUG_TB_ENABLED'])


if __name__ == '__main__':
    unittest.main()
