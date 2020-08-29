import http as code


class General4xx(BaseException):
    status = code.HTTPStatus.BAD_REQUEST

    def __init__(self, message=''):
        self.message = message

    def __str__(self):
        return "BAD REQUEST" + (' ' if self.message else '') + self.message


class HttpErrorUnauthorized(General4xx):
    status = code.HTTPStatus.UNAUTHORIZED

    def __init__(self, message=''):
        self.message = message

    def __str__(self):
        return "BAD REQUEST" + (' ' if self.message else '') + self.message


class HttpErrorNotFound(General4xx):
    status = code.HTTPStatus.NOT_FOUND


class HttpInvalidParam(General4xx):
    status = code.HTTPStatus.BAD_REQUEST

    def __init__(self, message=''):
        self.message = message

    def __str__(self):
        return "BAD REQUEST " + self.message


class HttpInternalServerError(BaseException):
    status = code.HTTPStatus.INTERNAL_SERVER_ERROR

    def __init__(self, message=''):
        self.message = message

    def __str__(self):
        return "Internal server error " + self.message
