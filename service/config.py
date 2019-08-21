import os


class BaseConfig:
    """Base configuration"""
    DEBUG = False
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY')
    DEBUG_TB_ENABLED = False
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    JWT_ACCESS_LIFESPAN = {'seconds': 30}
    JWT_REFRESH_LIFESPAN = {'minutes': 2}
    TOKEN_EXPIRATION_DAYS = 30
    TOKEN_EXPIRATION_SECONDS = 0
    PRAETORIAN_HASH_AUTOTEST = True


class DevelopmentConfig(BaseConfig):
    """Development configuration"""
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    JWT_ACCESS_LIFESPAN = {'seconds': 30}
    JWT_REFRESH_LIFESPAN = {'minutes': 2}
    DEBUG = True
    DEBUG_TB_ENABLED = True


class TestingConfig(BaseConfig):
    """Testing configuration"""
    TESTING = True
    SECRET_KEY = 'testing-and-thats-it'
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


class ProductionConfig(BaseConfig):
    """Production configuration"""
    DEBUG = False
    JWT_ACCESS_LIFESPAN = {'seconds': 0}
    JWT_REFRESH_LIFESPAN = {'minutes': 60}
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
