from werkzeug.exceptions import HTTPException as WerkzeugHTTPException

from app.logs import logger
from utils.response_helpers import (
    api_failure_response
)
from .base import APIError


def catch_app_error(error):
    message = APIError.message
    code = APIError.code

    if isinstance(error, APIError):
        message = error.message
        code = error.code
    elif isinstance(error, WerkzeugHTTPException):
        message = error.description
        code = error.code

    log_message = getattr(error, 'log_message', message)
    if log_message == APIError.message:
        log_message = 'Error: {0}'.format(error)

    logger.error('ABORT! {0}'.format(log_message), exc_info=True)

    return api_failure_response(
        error_msg=message,
        code=code
    )


def setup_error_handling(app):
    app.register_error_handler(APIError, catch_app_error)
    app.register_error_handler(WerkzeugHTTPException, catch_app_error)
    app.register_error_handler(Exception, catch_app_error)
