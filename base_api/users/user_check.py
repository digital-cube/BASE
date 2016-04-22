"""
Check if user is logged
"""
import base_common.msg
import base_common.app_hooks as apphooks
from base_config.service import log
from base_lookup import api_messages as msgs
from base_common.dbacommon import get_db
from base_common.dbacommon import app_api_method
from base_common.dbacommon import authenticated_call


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
    d['token'] = tk

    if hasattr(apphooks, 'extend_user_check'):
        _extend_res = apphooks.extend_user_check(dbuser)
        if _extend_res == False:
            log.critical('Error user check extending')
            return base_common.msg.error(msgs.ERROR_POST_CHECK)

        if isinstance(_extend_res, dict):
            d.update(_extend_res)

    return base_common.msg.post_ok(d)

