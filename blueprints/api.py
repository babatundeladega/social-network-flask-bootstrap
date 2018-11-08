from flask import Blueprint

from app.constants import APP_NAME
from utils.response_helpers import api_success_response


api_blueprint = Blueprint(__name__, 'api_blueprint', url_prefix='/api/v1.0')


@api_blueprint.route('/')
def render_welcome_greeting():
    return api_success_response("Welcome to {}".format(APP_NAME))


mappings = [

]


for url in mappings:
    path, view, name = url

    api_blueprint.add_url_rule(path, view_func=view.as_view(name))
