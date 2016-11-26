# coding= utf-8

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

log = retrieve_log(log_filename, log_logger)


def get_request_ip(request_handler):

    # INTENTIONALLY LEFT OUT OF EXCEPTION TO TRACK POSSIBLE EXCEPTIONS
    _proxy_ip = request_handler.request.headers
    _ip = _proxy_ip or request_handler.request.remote_ip

    return _ip


def format_password(username, password):

    return bcrypt.hashpw('{}{}'.format(username, password).encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def password_match(username, password, db_password):

    generated_password = '{}{}'.format(username, password).encode('utf-8')
    database_password = db_password.encode('utf-8')
    return database_password == bcrypt.hashpw(generated_password, database_password)
