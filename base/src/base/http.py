from http import HTTPStatus as status


class BaseHttpException(Exception):
    """
    Base Class for all HTTP Exceptions

    By default, the status property takes the 400 error status code until another one is supplied or assigned to it.

    Message and id_message are supplied on exception raising.
    """
    status = status.BAD_REQUEST

    def __init__(self, message: str = '', id_message: str = None, status: int = status.BAD_REQUEST):
        """
        Creates a Exception class object which is used for creating a Response when an Exception is raised.

        :param message: Untranslated message to be sent in the response
        :param id_message: Unique message key for translation or custom error messages to be sent in the response
        """
        self.message = message
        self.id_message = id_message

        BaseHttpException.status = status


class General4xx(BaseHttpException):
    """
    Exception class which is used for HTTP Error 400 - Bad Request.
    """
    status = status.BAD_REQUEST


class HttpErrorUnauthorized(BaseHttpException):
    """
    Exception class which is used for HTTP Error 401 - Unauthorized.
    """
    status = status.UNAUTHORIZED


class HttpErrorNotFound(BaseHttpException):
    """
    Exception class which is used for HTTP Error 404 - Not Found.
    """
    status = status.NOT_FOUND


class HttpInvalidParam(BaseHttpException):
    """
    Exception class which is used for HTTP Error 400 - Bad Request.

    Unlike the General4xx Class, this Exception is raised when a parameter was found by Base to have the wrong type or value.
    """
    status = status.BAD_REQUEST


class HttpInternalServerError(BaseHttpException):
    """
    Exception class which is used for HTTP Error 500 - Internal Server Error.
    """
    status = status.INTERNAL_SERVER_ERROR
