import os


# default config
class BaseConfig(object):
    DEBUG = False
    SECRET_KEY = os.environ["SECRET"]

    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}
    SQLALCHEMY_TRACK_MODIFICATIONS = False


# Unit test configurations
class TestConfig(BaseConfig):
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


# Development config
class DevelopmentConfig(BaseConfig):
    DEBUG = True
    REDIS_URL = os.environ["REDIS_URL"]
    try:
        SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
    except KeyError as e:
        SQLALCHEMY_DATABASE_URI = ''


# Production config
class ProductionConfig(BaseConfig):
    DEBUG = False
    REDIS_URL = os.environ["REDIS_URL"]
    try:
        SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
    except KeyError as e:
        SQLALCHEMY_DATABASE_URI = ''
