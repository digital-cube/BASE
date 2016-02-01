"""
User forgot password
"""

import json
import tornado.web
import base_common.msg
from base_lookup import api_messages as msgs
from base_common.dbacommon import app_api_method
from base_svc.comm import BaseAPIRequestHandler
from base_common.dbacommon import get_md2db
from base_common.dbacommon import check_user_exists
from base_config.service import support_mail

import base_api.hash2params.save_hash
import base_api.mail_api.save_mail


name = "Forgot password"
location = "user/password/forgot"
request_timeout = 10

password_change_uri = 'user/password/new'


def get_email_message(request, username, tk):

    m = """Dear {},<br/> follow the link bellow to change your password:<br/>http://{}/{}/{}""".format(
            username,
            request.request.host,
            password_change_uri,
            tk)

    return m


@app_api_method
def do_put(request, *args, **kwargs):
    """
    Forgot password
    :param username: users username, string, True
    :return:  200, OK
    :return:  404, notice
    """

    log = request.log
    _db = get_md2db()

    try:
        username = request.get_argument('username')
    except tornado.web.MissingArgumentError:
        log.critical('Missing argument username')
        return base_common.msg.error(msgs.MISSING_REQUEST_ARGUMENT)

    if not check_user_exists(username, _db, log):
        log.critical('User check fail')
        return base_common.msg.error(msgs.USER_NOT_FOUND)

    # GET HASH FOR FORGOTTEN PASSWORD
    rh = BaseAPIRequestHandler(log)
    data = {'cmd': 'forgot_password', 'username': username}
    rh.set_argument('data', json.dumps(data))
    res = base_api.hash2params.save_hash.do_put(rh)
    if 'http_status' not in res or res['http_status'] != 200:
        return base_common.msg.error('Cannot handle forgot password')

    tk = res['h']

    message = get_email_message(request, username, tk)

    # SAVE EMAIL FOR SENDING
    rh1 = BaseAPIRequestHandler(log)
    rh1.set_argument('sender', support_mail)
    rh1.set_argument('receiver', username)
    rh1.set_argument('message', message)
    res = base_api.mail_api.save_mail.do_put(rh1)
    if 'http_status' not in res or res['http_status'] != 204:
        return base_common.msg.error('Error finishing change password request')

    return base_common.msg.post_ok(msgs.OK)

