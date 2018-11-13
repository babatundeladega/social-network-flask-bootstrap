from .base import APIError, DEFAULT_ERROR_MESSAGE


_ERROR_CODE = 401


class AuthenticationError(APIError):
    code = _ERROR_CODE
    message = 'Unauthorized'  # 'An internal server error occurred!'


class InvalidAuthToken(AuthenticationError):
    message = 'Invalid authentication token provided.'


class TokenExpired(AuthenticationError):
    message = 'Token has expired.'


class UnauthorizedError(AuthenticationError):
    message = 'You are not authorized to make this request.'


class UnsuccessfulAuthentication(AuthenticationError):
    message = 'Authentication unsuccessful'
