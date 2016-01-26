"""
User login
"""
import tornado.web

import base_common.msg
from base_common.dbacommon import app_api_method
from base_common.dbacommon import format_password
from base_common.dbacommon import get_md2db
from base_common.dbacommon import qu_esc
from base_common.dbatokens import get_token
from base_common.seq import sequencer
from base_lookup import api_messages as msgs


name = "Login"
location = "user/login"
request_timeout = 10


@app_api_method
def do_post(request, *args, **kwargs):
    """
    User login
    :param username: users username, string, True
    :param password: users password, string, True
    :return:  200, OK
    :return:  404
    """

    log = request.log
    _db = get_md2db()
    dbc = _db.cursor()

    try:
        username = request.get_argument('username')
        password = request.get_argument('password')
    except tornado.web.MissingArgumentError:
        log.critical('Missing argument')
        return base_common.msg.error('Missing argument')

    password = format_password(username, password)

    q = "select id from users where username = '{}' and password = '{}'".format(
        qu_esc(username),
        qu_esc(password)
    )

    dbc.execute(q)
    if dbc.rowcount != 1:
        log.critical('{} users found: {}'.format(username, dbc.rowcount))
        return base_common.msg.error(msgs.USER_NOT_FOUND)

    u_id = dbc.fetchone()['id']

    # ASSIGN TOKEN
    tk = get_token(u_id, sequencer, dbc, log)
    if not tk:
        return base_common.msg.error('Cannot login user')

    _db.commit()

    return base_common.msg.post_ok({'token': tk})


