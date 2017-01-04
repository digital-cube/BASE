# coding= utf-8

import json
import bcrypt
import logging
from logging.handlers import TimedRotatingFileHandler

from base.config.settings import log_filename
from base.config.settings import log_logger

_logs = {}


def retrieve_log(log_file_name, _logger):

    if log_file_name in _logs:
        return _logs[log_file_name]

    _log_filename = log_file_name
    log_handler = TimedRotatingFileHandler(_log_filename, when="midnight")
    log_formatter = logging.Formatter(
        '%(asctime)-6s %(name)s %(module)s %(funcName)s %(lineno)d - %(levelname)s %(message)s')
    log_handler.setFormatter(log_formatter)

    _log = logging.getLogger(_logger)
    _log.propagate = False
    _log.addHandler(log_handler)
    _log.setLevel(logging.DEBUG)

    _logs[log_file_name] = _log

    return _log

log = None


def get_request_ip(request_handler):

    # INTENTIONALLY LEFT OUT OF EXCEPTION TO TRACK POSSIBLE EXCEPTIONS
    _proxy_ip = request_handler.request.headers.get('X-Forwarded-For')
    _ip = _proxy_ip or request_handler.request.remote_ip

    return _ip


def format_password(username, password):

    return bcrypt.hashpw('{}{}'.format(username, password).encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def password_match(username, password, db_password):

    generated_password = '{}{}'.format(username, password).encode('utf-8')
    database_password = db_password.encode('utf-8')
    return database_password == bcrypt.hashpw(generated_password, database_password)


def is_implemented(_target_class, _target_function_name, _target_function):

    if _target_function_name not in ('get', 'post', 'put', 'patch', 'delete'):
        return False

    from base.application.components import Base
    _base_function = getattr(Base, _target_function_name, None)
    if _base_function is None:
        return False

    if _target_function.__code__ == _base_function.__code__:
        return False

    return True


def client_call(url, port, location, method, data, headers=None, force_json=False):

    import http.client
    import urllib.parse
    conn = http.client.HTTPConnection(url, port)

    if force_json:
        body = json.dumps(data, ensure_ascii=False)
        _headers = {'content-type': 'application/json'}
    else:
        body = urllib.parse.urlencode(data)
        _headers = {'content-type': 'application/x-www-form-urlencoded'}

    if headers:
        _headers.update(headers)

    conn.request(method, location, body, headers=_headers)

    response = conn.getresponse()
    return response.read().decode('utf-8'), response.status

