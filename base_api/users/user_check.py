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
@app_api_method(
    method='POST',
    api_return=[(200, 'OK'), (400, '')]
)
def do_post(**kwargs):
    """
    Check if user is logged
    """

    _db = get_db()

    tk = kwargs['auth_token']
    from base_common.dbatokens import get_user_by_token
    dbuser = get_user_by_token(_db, tk)

    d = dbuser.dump_user()

    return base_common.msg.post_ok(d)

