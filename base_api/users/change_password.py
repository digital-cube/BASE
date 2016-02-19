"""
User change password
:description:
changing password from forgot password flow
or from user change password request
"""

import tornado.web
import base_common.msg
from base_lookup import api_messages as msgs
from base_common.dbacommon import format_password
from base_common.dbacommon import get_db
from base_common.dbacommon import app_api_method
from base_common.dbatokens import authorized_by_token
from base_common.dbatokens import get_user_by_token
from base_common.dbacommon import get_url_token
from base_common.dbacommon import check_password
from base_svc.comm import BaseAPIRequestHandler
import base_api.hash2params.retrieve_hash


name = "Change password"
location = "user/password/change.*"
request_timeout = 10


@app_api_method
def do_post(request, *args, **kwargs):
    """
    Change password
    :param newpassword: users newpassword, string, True
    :param oldpassword: old password if user logged, string, True
    :return:  200, OK
    :return:  404
    """

    log = request.log
    _db = get_db()
    dbc = _db.cursor()

    # TODO: check users token

    try:
        newpassword = request.get_argument('newpassword')
    except tornado.web.MissingArgumentError:
        log.critical('Missing argument password')
        return base_common.msg.error(msgs.MISSING_REQUEST_ARGUMENT)

    # CHANGE PASSWORD FROM FORGOT PASSWORD FLOW
    h2p = get_url_token(request, log)
    if h2p and len(h2p) > 60:

        rh = BaseAPIRequestHandler(log)
        rh.set_argument('hash', h2p)
        rh.r_ip= request.r_ip
        res = base_api.hash2params.retrieve_hash.do_get(rh)
        if 'http_status' not in res or res['http_status'] != 200:
            return base_common.msg.error(msgs.PASSWORD_TOKEN_EXPIRED)

        username = res['username']

    else:
        # TRY TO CHANGE PASSWORD FROM USER CHANGE REQUEST
        tk = request.auth_token
        if not authorized_by_token(_db, tk, log):
            return base_common.msg.error(msgs.UNAUTHORIZED_REQUEST)

        dbuser = get_user_by_token(_db, tk, log)
        if not dbuser.username:
            log.critical('User not found by token')
            return base_common.msg.error(msgs.UNAUTHORIZED_REQUEST)

        try:
            oldpassword = request.get_argument('oldpassword')
        except tornado.web.MissingArgumentError:
            log.critical('Missing argument oldpassword')
            return base_common.msg.error(msgs.MISSING_REQUEST_ARGUMENT)

        if not check_password(dbuser.password, dbuser.username, oldpassword):
            log.critical("Passwords don't match, entered : {}".format(oldpassword))
            return base_common.msg.error(msgs.WRONG_PASSWORD)

        username = dbuser.username

    # UPDATE USERS PASSWORD
    password = format_password(username, newpassword)

    uq = "update users set password = '{}' where username = '{}'".format(
        password,
        username
    )

    try:
        dbc.execute(uq)
    except Exception as e:
        log.critical('Change password: {}'.format(e))
        return base_common.msg.error(msgs.USER_PASSWORD_CHANGE_ERROR)

    _db.commit()

    return base_common.msg.post_ok(msgs.USER_PASSWORD_CHANGED)

