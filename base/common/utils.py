# coding= utf-8

import sys
import json
import bcrypt
import logging
from logging.handlers import TimedRotatingFileHandler


def user_exists(username, AuthUser, _session, as_bool=True):
    _q = _session.query(AuthUser).filter(AuthUser.username == username)
    return _q.count() == 1 if as_bool else _q.one_or_none()


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

    try:
        conn.request(method, location, body, headers=_headers)
    except ConnectionRefusedError as e:
        return 'Service not available', 503

    response = conn.getresponse()
    res = response.read().decode('utf-8'), response.status

    conn.close()

    return res


GOOGLE_DISCOVERY_DOCS = None


def get_google_discovery_docs():

    global GOOGLE_DISCOVERY_DOCS
    return GOOGLE_DISCOVERY_DOCS


def set_google_discovery_docs(docs):

    global GOOGLE_DISCOVERY_DOCS
    if GOOGLE_DISCOVERY_DOCS is None:
        GOOGLE_DISCOVERY_DOCS = docs


def check_facepy_library_installed():

    try:
        import facepy
    except ModuleNotFoundError:
        return False

    return 'facepy' in sys.modules


def check_slugify_library_installed():

    try:
        import slugify
    except ModuleNotFoundError:
        return False

    return 'slugify' in sys.modules


def check_timeago_library_installed():

    try:
        import timeago
    except ModuleNotFoundError:
        return False

    return 'timeago' in sys.modules


def update_entry_points(entries):
    '''
    Saves classes and method for URI and use it to create entry points in app configuration
    '''
    from base.config.application_config import entry_points_extended
    from base.config.application_config import balanced_readonly_get
    
    import inspect

    classes_with_read_only_methods = set()

    for b in balanced_readonly_get:
        class_name_and_function = str(b).split(' ')[1]
        class_name = class_name_and_function.split('.')[0]
        full_path = '{}.{}'.format(b.__module__,class_name)

        classes_with_read_only_methods.add(full_path)


    for e in entries:
        class_name = str(e[1]).split("'")[1]
        methods = {}

        for member in inspect.getmembers(e[1]):
            if member[0] in ('get', 'put', 'post', 'delete', 'patch'):
                methods[member[0]] = {'method': member[1]}

        entry_points_extended[class_name]={
            'uri': e[0],
            'class': e[1],
            'readonly': class_name in classes_with_read_only_methods,
            'methods': methods
        }



