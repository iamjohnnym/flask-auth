import os


class BaseConfig:
    """Base configuration"""
    DEBUG = False
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY')
    DEBUG_TB_ENABLED = False
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    JWT_ACCESS_LIFESPAN = {'seconds': 0}
    JWT_REFRESH_LIFESPAN = {'minutes': 15}
    SENTRY_URL = os.environ.get('SENTRY_URL')
    SENTRY_ENVIRONMENT = os.environ.get('SENTRY_ENVIRONMENT', 'base_config')


class DevelopmentConfig(BaseConfig):
    """Development configuration"""
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    JWT_ACCESS_LIFESPAN = {'seconds': 30}
    JWT_REFRESH_LIFESPAN = {'minutes': 2}
    DEBUG = True
    DEBUG_TB_ENABLED = True
    SENTRY_ENVIRONMENT = os.environ.get('SENTRY_ENVIRONMENT', 'development')


class TestingConfig(BaseConfig):
    """Testing configuration"""
    TESTING = True
    SECRET_KEY = 'testing-and-thats-it'  # nosec
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SENTRY_ENVIRONMENT = os.environ.get('SENTRY_ENVIRONMENT', 'testing')


class GithubTestingConfig(BaseConfig):
    """Testing configuration"""
    TESTING = True
    SECRET_KEY = 'testing-in-github-thats-it'  # nosec
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    # heh, sorry not sorry.
    SENTRY_ENVIRONMENT = \
        f"ghpr-{os.environ.get('GITHUB_REF', 'missing-ref').replace('/', '-')}"


class ProductionConfig(BaseConfig):
    """Production configuration"""
    DEBUG = False
    JWT_ACCESS_LIFESPAN = {'seconds': 0}
    JWT_REFRESH_LIFESPAN = {'minutes': 60}
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SENTRY_ENVIRONMENT = os.environ.get('SENTRY_ENVIRONMENT', 'production')
