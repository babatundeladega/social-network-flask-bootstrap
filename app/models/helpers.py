from flask import request
from . import APILog


def create_api_log():
    """Record API call and metadata."""
    from utils.contexts import get_current_request_data

    request_data = {
        'args': request.args,
        'body': get_current_request_data()
    }

    api_log = APILog(
        request_data=str(request_data),
        request_headers=str(request.headers)
    )
    api_log.save()

    return api_log
