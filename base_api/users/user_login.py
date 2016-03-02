"""
User login
"""
import tornado.web

import base_common.msg
import base_common.app_hooks as apphooks
from base_common.dbatokens import get_token
from base_common.dbacommon import get_db
from base_common.dbacommon import params
from base_common.dbacommon import app_api_method
from base_common.dbacommon import check_password
from base_lookup import api_messages as msgs


name = "Login"
location = "user/login"
request_timeout = 10


@app_api_method(method='POST')
@params(
    {'arg': 'username', 'type': 'e-mail', 'required': True},
    {'arg': 'password', 'type': str, 'required': True},
)
def do_post(request, *args, **kwargs):
    """
    User login
    :param username: users username, email, True
    :param password: users password, string, True
    :return:  200, OK
    :return:  404
    """

    log = request.log
    _db = get_db()
    dbc = _db.cursor()

    username, password = args

    q = apphooks.prepare_login_query(username)

    dbc.execute(q)
    if dbc.rowcount != 1:
        log.critical('{} users found: {}'.format(username, dbc.rowcount))
        return base_common.msg.error(msgs.USER_NOT_FOUND)

    us = dbc.fetchone()
    u_id = us['id']
    u_pwd = us['password']

    if not check_password(u_pwd, username, password):
        log.critical('Username {} wrong password: {}'.format(username, password))
        return base_common.msg.error(msgs.USER_NOT_FOUND)

    if hasattr(apphooks, 'login_expansion') and not apphooks.login_expansion(us):
        return base_common.msg.error(msgs.ERROR_LOGIN_USER)

    # ASSIGN TOKEN
    tk = get_token(u_id, dbc, log)
    if not tk:
        return base_common.msg.error(msgs.ERROR_LOGIN_USER)

    _db.commit()

    return base_common.msg.post_ok({'token': tk})


