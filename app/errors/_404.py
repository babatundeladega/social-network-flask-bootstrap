from .base import APIError, DEFAULT_ERROR_MESSAGE


_ERROR_CODE = 404


class ResourceNotFound(APIError):
    code = _ERROR_CODE
    message = 'Resource not found'


class DeletedResource(ResourceNotFound):
    message = 'Resource has been deleted'
