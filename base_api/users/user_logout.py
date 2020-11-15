# -*- coding: utf-8 -*-

"""
User logout
"""
from base_common.dbatokens import close_session_by_token
import base_common.msg
from base_lookup import api_messages as msgs
from base_common.dbacommon import get_db
from base_common.dbacommon import authenticated_call
from base_common.dbacommon import app_api_method
from base_config.service import log
import base_common.app_hooks as apphooks
from base_common.dbatokens import get_user_by_token
import base_config.settings as csettings
from base_lookup import authorization_type


name = "Logout"
location = "user/logout"
request_timeout = 10


@authenticated_call()
@app_api_method(
    method='POST',
    api_return=[(200, 'OK'), (404, '')]
)
def do_post(**kwargs):
    """
    Logout user
    """

    _db = get_db()
    dbc = _db.cursor()

    request = kwargs['request_handler']

    tk = request.auth_token

    dbuser = get_user_by_token(_db, tk)

    if not close_session_by_token(dbc, tk):
        log.warning("Closing session with token {}".format(tk))
        return base_common.msg.error(msgs.CLOSE_USER_SESSION)

    _db.commit()

    if hasattr(apphooks, 'post_logout_digest'):
        post_d = apphooks.post_logout_digest(_db, dbuser, tk)
        if post_d == False:
            log.critical('Error user post logout digest')
            return base_common.msg.error(msgs.ERROR_POST_LOGIN)

    if csettings.AUTHORIZATION_TYPE == authorization_type.rev[authorization_type.COOKIE]:
        kwargs['request_handler'].clear_cookie(csettings.SECURE_COOKIE)

    apphooks.action_log_hook(dbuser.id_user, kwargs['r_ip'], 'logout', 'user {} successfuly logged out'.format(dbuser.username))
    return base_common.msg.post_ok()

