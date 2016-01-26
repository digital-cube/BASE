"""
User registration
"""
import tornado.web
from MySQLdb import IntegrityError

import base_common.msg
from base_common.dbacommon import app_api_method
from base_common.dbacommon import format_password
from base_common.dbacommon import get_md2db
from base_common.dbacommon import qu_esc
from base_common.dbatokens import get_token
from base_common.seq import sequencer
from base_lookup import api_messages as msgs

name = "Registration"
location = "user/register"
request_timeout = 10


def check_user_registered(dbc,uname):

    q="select id from users where username = '{}'".format(qu_esc(uname))
    dbc.execute(q)
    return dbc.rowcount !=0


def prepare_user_query(u_id, username, password):

    q = "INSERT into users (id, username, password) VALUES " \
            "('{}', '{}', '{}')".format(
                qu_esc(u_id),
                qu_esc(username),
                qu_esc(password) )

    return q


@app_api_method
def do_post(request, *args, **kwargs):
    """
    Register user account
    :param username: users username, string, True
    :param password: users password, string, True
    :return:  201, Created
    :return:  404
    """

    log = request.log

    try:
        username = request.get_argument('username')
        password = request.get_argument('password')
    except tornado.web.MissingArgumentError:
        return base_common.msg.error('Missing arugment')

    password = format_password(username, password)

    _db = get_md2db()
    dbc = _db.cursor()

    if check_user_registered(dbc, username):
        return base_common.msg.error(msgs.USERNAME_ALREADY_TAKEN)

    u_id = sequencer.new('u')

    if not u_id:
        return base_common.msg.error('Error serializing user')

    quser = prepare_user_query(u_id, username, password)

    try:
        dbc.execute(quser)
    except IntegrityError as e:
        log.critical('User registration: {}'.format(e))
        return base_common.msg.error('User not registered')

    tk = get_token(u_id, sequencer, dbc, log)
    if not tk:
        return base_common.msg.error('Cannot login user')

    _db.commit()

    return base_common.msg.put_ok({'tk': tk}, http_status=201)


