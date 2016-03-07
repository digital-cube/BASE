"""
User registration
"""

import json
from MySQLdb import IntegrityError

import base_common.msg
import base_common.app_hooks as apphooks
from base_common.dbacommon import params
from base_common.dbacommon import app_api_method
from base_common.dbacommon import format_password
from base_common.dbacommon import get_db
from base_common.dbatokens import get_token
from base_common.seq import sequencer
from base_lookup import api_messages as msgs
from base_config.service import log

name = "Registration"
location = "user/register"
request_timeout = 10


def _check_user_registered(dbc, uname):

    q = "select id from users where username = '{}'".format(uname)
    dbc.execute(q)
    return dbc.rowcount != 0


@app_api_method(
    method='POST',
    api_return=[(201, 'Created'), (404, '')]
)
@params(
    {'arg': 'username', 'type': 'e-mail', 'required': True, 'description': 'users username'},
    {'arg': 'password', 'type': str, 'required': True, 'description': 'users password'},
    {'arg': 'data', 'type': json, 'required': False, 'description': 'application specific users data'},
)
def do_post(username, password, users_data, **kwargs):
    """
    Register user account
    """

    _db = get_db()
    dbc = _db.cursor()

    if _check_user_registered(dbc, username):
        return base_common.msg.error(msgs.USERNAME_ALREADY_TAKEN)

    if hasattr(apphooks, 'check_password_is_valid') and not apphooks.check_password_is_valid(password):
        return base_common.msg.error(msgs.INVALID_PASSWORD)

    password = format_password(username, password)

    u_id = sequencer().new('u')

    if not u_id:
        return base_common.msg.error(msgs.ERROR_SERIALIZE_USER)

    quser = apphooks.prepare_user_query(u_id, username, password, users_data, **kwargs)
    if not quser:
        log.critical('Error checking users data and create query')
        return base_common.msg.error(msgs.ERROR_REGISTER_USER)

    try:
        dbc.execute(quser)
    except IntegrityError as e:
        log.critical('User registration: {}'.format(e))
        return base_common.msg.error(msgs.ERROR_REGISTER_USER)

    tk = get_token(u_id, dbc)
    if not tk:
        return base_common.msg.error('Cannot login user')

    _db.commit()

    response = {'token': tk}

    if users_data and hasattr(apphooks, 'post_register_digest'):
        post_d = apphooks.post_register_digest(u_id, username, password, users_data, **kwargs)
        if post_d == False:
            log.critical('Error user post registration digest')
            return base_common.msg.error(msgs.ERROR_POST_REGISTRATION)

        if isinstance(post_d, dict):
            response.update(post_d)

    return base_common.msg.put_ok(response)


