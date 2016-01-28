"""
Check is user logged
"""
from base_common.dbatokens import authorized_by_token
from base_common.dbatokens import close_session_by_token
import base_common.msg
from base_lookup import api_messages as msgs
from base_common.dbacommon import get_md2db
from base_common.dbacommon import app_api_method
from base_common.dbacommon import qu_esc


name = "Check"
location = "user/check"
request_timeout = 10


@app_api_method
def do_post(request, *args, **kwargs):
    """
    User logout
    :param Auth: authorization token in header, string, True
    :return:  200, OK
    :return:  400
    """

    log = request.log

    _db = get_md2db()
    dbc = _db.cursor()

    tk = request.auth_token
    if not authorized_by_token(dbc, tk, log):
        return base_common.msg.error(msgs.UNAUTHORIZED_REQUEST)

    q = "select username from users u join session_token t on u.id = t.id_user where t.id = '{}'".format(qu_esc(tk))
    dbc.execute(q)

    if dbc.rowcount != 1:
        log.critical('Users {} found'.format(dbc.rowcount))
        return base_common.msg.error(msgs.USER_NOT_FOUND)

    db_user = dbc.fetchone()


    user = {'username':db_user['username']}


    return base_common.msg.post_ok(user)

