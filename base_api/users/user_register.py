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
from base_common.dbacommon import qu_esc
from base_common.dbatokens import get_token
from base_common.seq import sequencer
from base_lookup import api_messages as msgs

name = "Registration"
location = "user/register"
request_timeout = 10


def _check_user_registered(dbc, uname):

    q = "select id from users where username = '{}'".format(qu_esc(uname))
    dbc.execute(q)
    return dbc.rowcount != 0


@app_api_method
@params(
    {'arg': 'username', 'type': 'e-mail', 'required': True},
    {'arg': 'password', 'type': str, 'required': True},
    {'arg': 'data', 'type': json, 'required': False},
)
def do_post(_, *args, **kwargs):
    """
    Register user account
    :param username: users username, string, True
    :param password: users password, string, True
    :param user_data: application specific users data, string, False
    :return:  201, Created
    :return:  404
    """

    log = _.log

    username, password, users_data = args
    username = qu_esc(username)

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

    quser = apphooks.prepare_user_query(u_id, username, password, users_data, log)
    if not quser:
        log.critical('Error checking users data and create query')
        return base_common.msg.error(msgs.ERROR_REGISTER_USER)

    try:
        dbc.execute(quser)
    except IntegrityError as e:
        log.critical('User registration: {}'.format(e))
        return base_common.msg.error(msgs.ERROR_REGISTER_USER)

    tk = get_token(u_id, dbc, log)
    if not tk:
        return base_common.msg.error('Cannot login user')

    _db.commit()

    response = {'token': tk}

    if users_data and hasattr(apphooks, 'post_register_digest'):
        response.update(apphooks.post_register_digest(u_id, username, password, users_data))

    return base_common.msg.put_ok(response)


