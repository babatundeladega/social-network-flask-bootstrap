from .base import APIError, DEFAULT_ERROR_MESSAGE


_ERROR_CODE = 500


class InternalServerError(APIError):
    code = _ERROR_CODE
    message = DEFAULT_ERROR_MESSAGE  # 'An internal server error occurred!'
