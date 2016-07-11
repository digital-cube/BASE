# -*- coding: utf-8 -*-

"""
User forgot password
"""

import json
import base_common.msg
from base_config.service import log
from base_lookup import api_messages as msgs
from base_common.dbacommon import params
from base_common.dbacommon import app_api_method
from base_svc.comm import BaseAPIRequestHandler
from base_common.dbacommon import get_db
from base_common.dbacommon import check_user_exists
from base_config.service import support_mail

import base_api.hash2params.save_hash
import base_api.mail_api.save_mail
from base_common.app_hooks import forgot_password_hook


name = "Forgot password"
location = "user/password/forgot"
request_timeout = 10

# password_change_uri = 'user/password/new'
# def get_email_message(request, username,
# #tk):
#
#     m = """Dear {},<br/> follow the link bellow to change your password:<br/>http://{}/{}/{}""".format(
#             username,
#             request.request.host,
#             password_change_uri,
#             tk)
#
#     return m


@app_api_method(
    method='PUT',
    api_return=[(200, 'OK'), (404, '')]
)
@params(
    {'arg': 'username', 'type': 'e-mail', 'required': True, 'description': 'users username'},
)
def do_put(username, *args, **kwargs):
    """
    Forgot password
    """

    _db = get_db()

    request = kwargs['request_handler']

    if not check_user_exists(username, _db):
        log.critical('User check fail')
        return base_common.msg.error(msgs.USER_NOT_FOUND)

    # GET HASH FOR FORGOTTEN PASSWORD
    rh = BaseAPIRequestHandler()
    data = {'cmd': 'forgot_password', 'username': username}
    rh.set_argument('data', json.dumps(data, ensure_ascii=False))
    kwargs['request_handler'] = rh
    res = base_api.hash2params.save_hash.do_put(json.dumps(data, ensure_ascii=False), *args, **kwargs)
    if 'http_status' not in res or res['http_status'] != 200:
        return base_common.msg.error('Cannot handle forgot password')

    tk = res['h']

    if not forgot_password_hook(request, username, tk, **kwargs):
        log.critical('Error finishing username change process')
        return base_common.msg.error(msgs.ERROR_PASSWORD_RESTORE)

    #
    # message = get_email_message(request, username, tk)
    #
    # # SAVE EMAIL FOR SENDING
    # rh1 = BaseAPIRequestHandler()
    # rh1.set_argument('sender', support_mail)
    # rh1.set_argument('receiver', username)
    # rh1.set_argument('message', message)
    # kwargs['request_handler'] = rh1
    # res = base_api.mail_api.save_mail.do_put(support_mail, username, message, *args, **kwargs)
    # if 'http_status' not in res or res['http_status'] != 204:
    #     return base_common.msg.error('Error finishing change password request')

    return base_common.msg.post_ok(msgs.OK)

