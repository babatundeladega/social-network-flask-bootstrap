DEFAULT_ERROR_CODE = 500  # internal server error
DEFAULT_ERROR_MESSAGE = (
    'Server cannot validate requests sent at this time, please try again.'
)


class APIError(Exception):
    """Base exception for all exceptions"""

    code = DEFAULT_ERROR_CODE
    message = DEFAULT_ERROR_MESSAGE

    def __init__(self, message=None, code=None, log_message=None):
        self.message = (
            message or getattr(self.__class__, 'message',
                               DEFAULT_ERROR_MESSAGE)
        )
        self.code = (
            code or getattr(self.__class__, 'code', DEFAULT_ERROR_CODE)
        )
        self.log_message = log_message or self.message
