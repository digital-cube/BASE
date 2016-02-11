import os
import sys
import bcrypt
import MySQLdb
import MySQLdb.cursors
from functools import wraps
from MySQLdb import IntegrityError

import base_config.settings
import base_common.msg
from base_common.dbaexc import ApiMethodError, ApplicationDbConfig
from base_lookup import api_messages as amsgs


__db = None


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


def app_api_method(origin_f):
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
            raise ApiMethodError('{}, {}, {}, {}'.format(exc_type, fname, exc_tb.tb_lineno, str(e)))

    return f_wrapper


def authenticated_call(original_f):
    """
    Checking if user who calls authenticated
    :param original_f:  function to be called
    :return:  function or error
    """
    @wraps(original_f)
    def f_wrapper(request_handler, *args,**kwargs):

        if not hasattr(request_handler, 'auth_token'):
            return base_common.msg.error(amsgs.UNAUTHORIZED_REQUEST)

        tk = request_handler.auth_token
        _db = get_db()
        dbc = _db.cursor()
        log = request_handler.log

        from base_common.dbatokens import authorized_by_token
        if not authorized_by_token(dbc, tk, log):
            return base_common.msg.error(amsgs.UNAUTHORIZED_REQUEST)

        return original_f(request_handler, *args, **kwargs)

    return f_wrapper


def check_user_exists(username, db, log, userid=None):
    dbc = db.cursor()
    if userid:
        q = "select id from users where id = '{}'".format(qu_esc(userid))
    else:
        q = "select id from users where username = '{}'".format(qu_esc(username))

    try:
        dbc.execute(q)
    except IntegrityError as e:
        log.critical('Check user: {}'.format(e))
        return False

    if dbc.rowcount != 1:
        log.warning('Fund {} users with {} username'.format(dbc.rowcount, username))
        return False

    return True


def get_auth_token(request_handler, log):

    tk = None
    if 'Authorization' in request_handler.request.headers:
        tka = request_handler.request.headers.get('Authorization')
        tka = tka.split(' ')
        if len(tka) == 1:
            tk = tka[0].strip()

    return tk


def get_url_token(request_handler, log):

    tk = None
    url_parts = request_handler.request.uri.split('/')
    if url_parts:
        tk = url_parts[-1]

    return tk
