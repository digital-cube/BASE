"""
Check if user is logged
"""
from base_common.dbacommon import authenticated_call
import base_common.msg
from base_common.dbacommon import get_db
from base_common.dbacommon import app_api_method


name = "Check"
location = "user/check"
request_timeout = 10


@authenticated_call()
@app_api_method
def do_post(request, *args, **kwargs):
    """
    Check if user is logged
    :Authorization: token required
    :return:  200, OK
    :return:  400
    """

    log = request.log

    _db = get_db()

    tk = request.auth_token
    from base_common.dbatokens import get_user_by_token
    dbuser = get_user_by_token(_db, tk, log)

    d = dbuser.dump_user()

    return base_common.msg.post_ok(d)

