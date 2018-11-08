from .base import APIError, DEFAULT_ERROR_MESSAGE


_ERROR_CODE = 403


class ForbiddenError(APIError):
    code = _ERROR_CODE
    message = 'Forbidden request'  # 'An internal server error occurred!'


class BadRequest(ForbiddenError):
    message = 'Bad request'


class InsufficientFunds(ForbiddenError):
    message = 'Insufficient funds'


class AttributeError(ForbiddenError):
    message = 'Resource does not have request attribute'


class ResourcesNotRelated(ForbiddenError):
    message = 'Resources not related'


class ResourceConflict(ForbiddenError):
    message = 'Resource already exists'
