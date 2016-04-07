import os
import sys
import ast
import json
import json.decoder
import redis
import decimal
import bcrypt
import datetime
import MySQLdb
import MySQLdb.cursors
from functools import wraps
from MySQLdb import IntegrityError

import base_config.settings
import base_common.msg
import base_lookup.http_methods as _hm
from base_common.dbaexc import ApplicationDbConfig
from base_lookup import api_messages as amsgs
from base_config.service import log
from base_config.settings import REDIS_SERVER, REDIS_PORT


__db = None
__redis = None


def get_db(prefix=None):
    global __db

    host = base_config.settings.APP_DB.host
    user = base_config.settings.APP_DB.user
    passwd = base_config.settings.APP_DB.passwd
    db = '{}{}'.format(prefix, base_config.settings.APP_DB.db) if prefix else base_config.settings.APP_DB.db
    charset = base_config.settings.APP_DB.charset

    def conn_to_db():

        return MySQLdb.connect(
                host=host,
                user=user,
                passwd=passwd,
                db=db,
                charset=charset,
                cursorclass=MySQLdb.cursors.DictCursor)

    def test_db_conn(db):
        try:
            db.cursor().execute('select 1')
        except MySQLdb.OperationalError as e:
            if len(e.args) == 2 and e.args[0] == 2006 and e.args[1] == 'MySQL server has gone away':
                return False
            raise ApplicationDbConfig('Operational error occur: {}'.format(e))
        return True

    if __db and __db.open:
        if not test_db_conn(__db):
            __db = conn_to_db()
        return __db

    __db = conn_to_db()

    return __db


def get_redis_db():

    global __redis

    if __redis:
        return __redis

    __redis = redis.Redis(host=REDIS_SERVER, port=REDIS_PORT)

    return __redis


def close_stdout(debug):
    if not debug:
        null = '/dev/null' if os.name == 'posix' else 'null'
        n = open(null, 'w')
        sys.stdout = n
        sys.stderr = n


def qu_esc(query):
    return MySQLdb.escape_string(query).decode('utf-8')


def format_password(username, password):

    return bcrypt.hashpw('{}{}'.format(username, password).encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def check_password(db_pwd, username, password):

    pwd = '{}{}'.format(username, password).encode('utf-8')
    dpwd = db_pwd.encode('utf-8')
    return dpwd == bcrypt.hashpw(pwd, dpwd)


def app_api_method(**arguments):

    def o_wrapper(origin_f):
        """
        Decorator for every get/post/put/delete method
        """

        @wraps(origin_f)
        def f_wrapper(*args, **kwargs):

            try:
                return origin_f(*args, **kwargs)
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]

                _list = '{}({})'.format(fname, exc_tb.tb_lineno)
                _n = exc_tb.tb_next
                _c = None
                while _n:
                    _fname = os.path.split(_n.tb_frame.f_code.co_filename)[1]
                    _list += ' -> {}({})'.format(_fname, _n.tb_lineno)
                    _c = '{}({})'.format(_n.tb_frame.f_code.co_name, _n.tb_lineno)
                    _n = _n.tb_next

                import inspect
                parent_module = inspect.getmodule(origin_f)
                log.critical('{} -> {} -> {} -> {} -> {}'.format(
                    parent_module.__name__, str(e), _list, origin_f.__name__, _c))

                return base_common.msg.error(amsgs.API_CALL_EXCEPTION)

        # set api method meta data
        f_wrapper.__api_method_call__ = arguments['expose'] if 'expose' in arguments else True
        f_wrapper.__api_method_type__ = arguments['method'] if 'method' in arguments else _hm.rev[_hm.GET]
        f_wrapper.__api_path__ = arguments['uri'] if 'uri' in arguments else ''
        f_wrapper.__api_return__ = arguments['api_return'] if 'api_return' in arguments else []
        f_wrapper.__api_return_type__ = arguments['return_type'] if 'return_type' in arguments else []

        return f_wrapper

    return o_wrapper


def authenticated_call(*arguments):
    """
    Checking if user who calls authenticated
    :param original_f:  function to be called
    :return:  function or error
    """

    def outer_wrapper(original_f):

        @wraps(original_f)
        def f_wrapper(*args, **kwargs):

            request_handler = kwargs['request_handler']

            if not hasattr(request_handler, 'auth_token'):
                return base_common.msg.error(amsgs.UNAUTHORIZED_REQUEST)

            from base_config import settings as base_settings
            if not base_settings.APP_DB:
                return base_common.msg.error(amsgs.UNAUTHORIZED_REQUEST)

            tk = request_handler.auth_token
            _db = get_db()

            from base_common.dbatokens import authorized_by_token
            if not authorized_by_token(_db, tk):
                log.critical("Unauthorized access attempt")
                return base_common.msg.error(amsgs.UNAUTHORIZED_REQUEST)

            from base_common.dbatokens import get_user_by_token
            dbuser = get_user_by_token(_db, tk)

            _access = (len(arguments) == 0)
            for a in arguments:

                if bool(dbuser.role&a):
                    _access = True

            if not _access:
                log.critical("Unauthorized user access attempt")
                return base_common.msg.error(amsgs.UNAUTHORIZED_REQUEST)

            return original_f(*args, **kwargs)

        f_wrapper.__api_authenticated__ = True

        return f_wrapper

    return outer_wrapper


def check_user_exists(username, db, userid=None):
    dbc = db.cursor()
    if userid:
        q = "select id from users where id = '{}'".format(userid)
    else:
        q = "select id from users where username = '{}'".format(username)

    try:
        dbc.execute(q)
    except IntegrityError as e:
        log.critical('Check user: {}'.format(e))
        return False

    if dbc.rowcount != 1:
        log.warning('Fund {} users with {} username'.format(dbc.rowcount, username))
        return False

    return True


def get_url_token(request_handler):

    tk = None
    url_parts = request_handler.request.uri.split('/')
    if url_parts:
        tk = url_parts[-1]

    return tk


def _convert_args(el, tp, esc):

    if tp == int:

        if el == '0':
            return 0

        try:
            el = int(el)
        except ValueError as e:
            log.critical('Invalid argument: expected int got {} ({}): {}'.format(el, type(el), e))
            return False

        return el

    if tp == float:
        try:
            el = float(el)
        except ValueError as e:
            log.critical('Invalid argument: expected float got {} ({}): {}'.format(el, type(el), e))
            return False

        return el

    if tp == str:

        if type(el) != str:
            return False

        return qu_esc(el) if esc else el

    if tp == datetime.datetime:

        try:
            el = datetime.datetime.strptime(el, "%Y-%m-%d %H:%M:%S")
        except ValueError as e:
            log.critical('Invalid argument: expected datetime got {} ({}): {}'.format(el, type(el), e))
            return False

        return str(el)[:19]

    if tp == datetime.date:

        try:
            el = datetime.datetime.strptime(el, "%Y-%m-%d")
        except ValueError as e:
            log.critical('Invalid argument: expected date got {} ({}): {}'.format(el, type(el), e))
            return False

        return str(el)[:10]

    if tp == json:

        try:
            el = json.dumps(json.loads(el))
        except json.decoder.JSONDecodeError as e:
            log.critical('Invalid argument: expected json got {} ({}): {}'.format(el, type(el), e))
            return False

        return qu_esc(el) if esc else el

    if tp == 'e-mail':

        if '@' not in el:
            log.critical('Invalid argument: expected e-mail address, got {}'.format(el))
            return False

        return qu_esc(el) if esc else el

    if tp == list:

        try:
            el = ast.literal_eval(el)
        except SyntaxError as e:
            log.critical('Invalid argument: expected list, got {}: {}'.format(el, e))
            return False

        if type(el) != list:
            return False

        return el

    if tp == dict:

        try:
            el = ast.literal_eval(el)
        except SyntaxError as e:
            log.critical('Invalid argument: expected dict, got {}: {}'.format(el, e))
            return False

        if type(el) != dict:
            return False

        return el

    if tp == bool:

        try:
            return el.lower() == 'true'
        except AttributeError:
            return isinstance(el, bool) and el

    if tp == decimal.Decimal:

        try:
            el = decimal.Decimal(el)
        except decimal.InvalidOperation as e:
            log.critical('Invalid argument: expected Decimal, got {}: {}'.format(el, e))
            return False

        return el


def _tr_type(t):
    if t == str:
        return 'string'
    if t == int:
        return 'integer'
    if t == float:
        return 'float'
    if t == json:
        return 'json'
    if t == datetime.date:
        return 'date'
    if t == datetime.datetime:
        return 'datetime'
    if t == bool:
        return 'boolean'
    return 'Unkonwn type'


def params(*arguments):

    def real_dec(original):

        desc_args = []
        for _a in arguments:
            desc_args.append([
                _a['arg'],
                _a['description'] if 'description' in _a else 'Missing description',
                _tr_type(_a['type'] if 'type' in _a else str),
                _a['required'] if 'required' in _a else None,
                _a['example'] if 'example' in _a else None
            ])

        @wraps(original)
        def wrapper(*args, **kwargs):

            ags = []
            request = kwargs['request_handler']

            for a in arguments:

                default_arg_value = a['default'] if 'default' in a else None
                argmnt = a['arg'].strip()

                atr = request.get_argument(argmnt, default=default_arg_value)

                required = a['required'] if 'required' in a else True

                if not atr:
                    if not required:
                        converted = None
                    else:
                        log.critical('Missing request argument: {}'.format(argmnt))
                        return base_common.msg.error(amsgs.MISSING_REQUEST_ARGUMENT)
                else:
                    tip = a['type'] if 'type' in a else str
                    esc = a['escaped'] if 'escaped' in a else (tip in [str, 'e-mail'])

                    converted = _convert_args(atr, tip, esc)
                    if not converted:

                        if not (tip == int and converted != 0):   # count 0 as int

                            c_type = "|type get error|"
                            try:
                                c_type = type(atr)
                            except Exception as e:
                                log.warning('Get argument type error: {}'.format(e))

                            log.critical('Invalid request argument {} type {}, expected {}'.format(atr, c_type, tip))
                            return base_common.msg.error(amsgs.INVALID_REQUEST_ARGUMENT)

                ags.append(converted)

            return original(*ags, **kwargs)

        wrapper.__app_api_arguments__ = desc_args

        return wrapper

    return real_dec


def get_current_datetime():

    _db = get_db()
    dbc = _db.cursor()
    _t = 'test_datetime'

    if base_config.settings.TEST_MODE:
        q = '''SELECT o_value FROM options where o_key = '{}' '''.format(_t)
        try:
            dbc.execute(q)
        except IntegrityError as e:
            log.critical('Error reading {} from database: {}'.format(_t, e))
            return datetime.datetime.now()

        if dbc.rowcount != 1:
            log.warning('Found {} current date occurrences'.format(dbc.rowcount))
            return datetime.datetime.now()

        _td = dbc.fetchone()

        try:
            _td_datetime = datetime.datetime.strptime(_td['o_value'], '%Y-%m-%d %H:%M:%S.%f')
        except ValueError as e:
            log.critical('Error creating datetime from {}: {}'.format(_td['o_value'], e))
            return datetime.datetime.now()

        return _td_datetime

