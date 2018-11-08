"""A generic flask repository for social networks"""
import asyncio

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from config import get_configuration_class
from .logs import logger
from .errors.handlers import setup_error_handling
from .gateways.messaging_client.contrib.flask import MessagingAPIClient
from utils.contexts.handlers import before_every_request, after_every_request


asyncio_loop = asyncio.get_event_loop()
config_object = get_configuration_class()


db = SQLAlchemy()
messaging_api_client = MessagingAPIClient()


def _bind_request_contexts_handlers(app, blueprint):
    # Bind before and after request context handlers to blueprint

    app.before_request_funcs.setdefault(
        blueprint.name, []).insert(0, before_every_request)
    app.after_request_funcs.setdefault(
        blueprint.name, []).insert(0, after_every_request)


def _setup_blueprints(app):
    from blueprints import api_blueprint

    app.register_blueprint(api_blueprint)

    _bind_request_contexts_handlers(app, api_blueprint)


def create_app():
    app = Flask(__name__)
    app.config.from_object(config_object)

    _setup_blueprints(app)
    setup_error_handling(app)

    db.init_app(app)
    messaging_api_client.init_app(app)

    return app
