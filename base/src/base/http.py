from http import HTTPStatus as status


class BaseHttpException(Exception):
    """
    Base Class for all HTTP Exceptions

    By default, the status property takes the 400 error status code until another one is supplied or assigned to it.

    Message and id_message are supplied on exception raising.
    """
    _status = status.BAD_REQUEST

    def __init__(self, message: str = '', id_message: str = None, status: int = status.BAD_REQUEST, **kwargs):
        """
        Creates a Exception class object which is used for creating a Response when an Exception is raised.

        :param message: Untranslated message to be sent in the response
        :param id_message: Unique message key for translation or custom error messages to be sent in the response
        """
        self.message = message
        self.id_message = id_message

        BaseHttpException._status = status
        self._status = int(status)

        self.kwargs = kwargs

    def status(self):
        return self._status

    def _dict(self):
        r = {}
        if self.message:
            r.update({'message': self.message})
        if self.id_message:
            r.update({'id': self.id_message})
        if self._status:
            r.update({'code': self._status})

        for arg in self.kwargs:
            r.update({arg: self.kwargs[arg]})

        return r

class General4xx(BaseHttpException):
    """
    Exception class which is used for HTTP Error 400 - Bad Request.
    """
    _status = status.BAD_REQUEST

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._status = status.BAD_REQUEST


class HttpErrorUnauthorized(BaseHttpException):
    """
    Exception class which is used for HTTP Error 401 - Unauthorized.
    """
    _status = status.UNAUTHORIZED

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._status = status.UNAUTHORIZED


class HttpErrorForbiden(BaseHttpException):
    """
    Exception class which is used for HTTP Error 403 - Forbidden.
    """
    _status = status.FORBIDDEN

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._status = status.FORBIDDEN



class HttpErrorNotFound(BaseHttpException):
    """
    Exception class which is used for HTTP Error 404 - Not Found.
    """
    _status = status.NOT_FOUND

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._status = status.NOT_FOUND



class HttpNotAcceptable(BaseHttpException):
    """
    Exception class which is used for HTTP Error 406 - Not Acceptable.
    """
    _status = status.NOT_ACCEPTABLE

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._status = status.NOT_ACCEPTABLE



class HttpInvalidParam(BaseHttpException):
    """
    Exception class which is used for HTTP Error 400 - Bad Request.

    Unlike the General4xx Class, this Exception is raised when a parameter was found by Base to have the wrong type or value.
    """
    _status = status.BAD_REQUEST

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._status = status.BAD_REQUEST


class HttpInternalServerError(BaseHttpException):
    """
    Exception class which is used for HTTP Error 500 - Internal Server Error.
    """
    _status = status.INTERNAL_SERVER_ERROR

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._status = status.INTERNAL_SERVER_ERROR

class IPCException(HttpInternalServerError):

    pass