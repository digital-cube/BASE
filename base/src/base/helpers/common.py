import bcrypt
import datetime


def format_password(username, password):
    """
    Format user's password, salt it with the username.
    For changing the username there has to be a password provided
    :param username: user's username
    :param password: user's password
    :return: bcrypt-ed password
    """

    return bcrypt.hashpw('{}{}'.format(username, password).encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def password_match(username, password, db_password) -> bool:
    """
    Check if the user's provided password match the one in the database, with bcrypt
    :param username: provided by an user
    :param password: provided by an user
    :param db_password: user's bcrypt-ed password from the database
    :return: True if provided credentials match, otherwise False
    """

    generated_password = '{}{}'.format(username, password).encode('utf-8')
    database_password = db_password.encode('utf-8')
    return database_password == bcrypt.hashpw(generated_password, database_password)


def get_request_ip(request_handler):
    """
    Get the IP address from request handler object
    :param request_handler: request handler object
    :return: IP address string
    """
    _proxy_ip = request_handler.request.headers.get('X-Forwarded-For')
    _ip = _proxy_ip or request_handler.request.remote_ip
    return _ip


def filter_only_allowed_keys(allowed: list, source: list):
    source = set(source if source else [])

    return [k for k in allowed if k in source]


def missing_keys(source, expected_keys: list):
    if not source:
        return expected_keys

    missing = []
    for key in expected_keys:
        if key not in source:
            missing.append(key)

    return missing


def fdate(s):
    if type(s) == datetime.datetime:
        return s.date()
    if type(s) == datetime.date:
        return s
    return 'N/A'
