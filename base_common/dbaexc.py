
class ToManyAttemptsException(Exception):
    """
    Number of attempts excited. For db insertions and others.
    """

    def __init__(self, message):
        super(Exception, self).__init__(message)


class ErrorRetrieveId(Exception):
    """
    Can't retrieve id from table
    """

    def __init__(self, message):
        super(Exception, self).__init__(message)


class ErrorRetrieveUserId(Exception):
    """
    Can't retrieve user id from db
    """

    def __init__(self, message):
        super(Exception, self).__init__(message)


class ErrorRetrieveSessionToken(Exception):
    """
    Can't retrieve session id from db
    """

    def __init__(self, message):
        super(Exception, self).__init__(message)


class ErrorSetSessionToken(Exception):
    """
    Can't set session token
    """

    def __init__(self, message):
        super(Exception, self).__init__(message)


class ApiMethodError(Exception):
    """
    Applications method error
    """

    def __init__(self, message):
        super(Exception, self).__init__(message)


class ApplicationDbConfig(Exception):
    """
    Application's DB not configured
    """

    def __init__(self, message):
        super(Exception, self).__init__(message)


class ApplicationNameUsed(Exception):
    """
    Application's name already exists
    """

    def __init__(self, message):
        super(Exception, self).__init__(message)
