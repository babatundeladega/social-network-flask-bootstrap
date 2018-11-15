import os

from app.constants import APP_NAME


class DevelopmentConfig(object):
    DEBUG = True

    APP_NAME = ''
    API_REQUESTS_TIMEOUT = 30

    MESSAGING_API_KEY = 'Ai48NVEN6fBbwHbQAWfEFP'
    MESSAGING_API_AUTH_USERNAME = '07085121508'
    MESSAGING_API_AUTH_PASSWORD = os.environ['MESSAGING_API_AUTH_PASSWORD']

    SECURITY_PASSWORD_SALT = '5a581dcf-363d-4e1e-a9d5-4ecf384c5b5f'
    SECRET_KEY = b'\x92B\xe08\x86\x11bY\x84\x90\x81G\x8cZ5v6>'

    SERVER_NAME = 'localhost:5009'

    SQLALCHEMY_DATABASE_URI = (
        'mysql+pymysql://tomisin:tomisin10@localhost/{}_dev'.format(
            APP_NAME.lower())
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class ProductionConfig(object):
    APP_NAME = ''
    API_REQUESTS_TIMEOUT = 30

    MESSAGING_API_KEY = ''
    MESSAGING_API_AUTH_USERNAME = ''
    MESSAGING_API_AUTH_PASSWORD = os.environ['MESSAGING_API_AUTH_PASSWORD']

    SECURITY_PASSWORD_SALT = ''
    SECRET_KEY = b''

    SQLALCHEMY_DATABASE_URI = ''
    SQLALCHEMY_TRACK_MODIFICATIONS = False


config_objects = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}


def get_configuration_class():
    return config_objects[os.environ['RUNNING_MODE']]
