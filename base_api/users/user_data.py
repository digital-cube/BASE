"""
Check is user logged
"""
from base_common.dbacommon import authenticated_call
import base_common.msg
from base_lookup import api_messages as amsgs
from base_common.dbacommon import get_db
from base_common.dbacommon import app_api_method
from base_common.dbacommon import qu_esc


name = "User data"
location = "user/data"
request_timeout = 10


@authenticated_call()
@app_api_method
def do_get(request, *args, **kwargs):
    """
    Get user data
    :Authorization: token required
    :param username: requested user username, string, True
    :return:  200, OK
    :return:  400
    """

    log = request.log

    _db = get_db()
    dbc = _db.cursor()

    username = request.get_argument('username', default='')
    username = qu_esc(username)

    q = "select id, username from users where username = '{}'".format(username)
    dbc.execute(q)

    if dbc.rowcount != 1:
        log.critical('Users {} found'.format(dbc.rowcount))
        return base_common.msg.error(amsgs.USER_NOT_FOUND)

    db_user = dbc.fetchone()

    user = {'uid': db_user['id'], 'username': db_user['username']}

    return base_common.msg.post_ok(user)

