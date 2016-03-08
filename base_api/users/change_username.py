"""
User change email
:description:
user change the username (email)
"""

import json
import base_common.msg
import base_api.hash2params.save_hash
import base_api.mail_api.save_mail
from base_config.service import log
from base_lookup import api_messages as msgs
from base_common.dbacommon import check_password
from base_common.dbacommon import get_db
from base_common.dbacommon import params
from base_common.dbacommon import app_api_method
from base_common.dbacommon import authenticated_call
from base_common.dbatokens import get_user_by_token
from base_svc.comm import BaseAPIRequestHandler
from base_config.service import support_mail
import base_api.users.changing_username


name = "Change username"
location = "user/username/change"
request_timeout = 10


def _get_email_warning(oldusername, newusername):
    """
    Create warning email for old username
    :param request:  request handler
    :param oldusername:  old username
    :param newusername:  new username
    :param h:  hash
    :return:  message as string
    """
    m = '''Dear,<br/>we have receive request for changing username {} to {}.<br/> If You request the change take no
    further actions.<br/>If this action is not performed by You please contact our support at {}.
    Thank you for using {}'''.format(oldusername, newusername, support_mail, 'our services.')

    return m


def _get_email_message(request, h):
    """
    Create email message
    :param request:  request handler
    :param oldusername:  old username
    :param newusername:  new username
    :param h:  hash for change
    :return:  message text as string
    """

    l = 'http://{}/{}{}'.format(request.request.host, base_api.users.changing_username.location[:-2], h)
    m = '''Dear,<br/>You have requested username change. Please confirm change by following the link below:<br/>
    {}<br/><br/>If You didn't requested the change, please ignore this message.<br/>Thank You!'''.format(l)

    return m


@authenticated_call()
@app_api_method(
    method='POST',
    api_return=[(200, 'OK'), (404, '')]
)
@params(
    {'arg': 'username', 'type': 'e-mail', 'required': True, 'description': 'users new username'},
    {'arg': 'password', 'type': str, 'required': True, 'description': 'users password'},
)
def do_post(newusername, password, **kwargs):
    """
    Change password
    """

    _db = get_db()

    request = kwargs['request_handler']
    tk = kwargs['auth_token']

    dbuser = get_user_by_token(_db, tk)

    if not check_password(dbuser.password, dbuser.username, password):
        log.critical('Wrong users password: {}'.format(password))
        return base_common.msg.error(msgs.WRONG_PASSWORD)

    # SAVE HASH FOR USERNAME CHANGE
    rh = BaseAPIRequestHandler()
    data = {'cmd': 'change_username', 'newusername': newusername, 'user_id': dbuser.user_id, 'password': password}
    rh.set_argument('data', json.dumps(data))
    kwargs['request_handler'] = rh
    res = base_api.hash2params.save_hash.do_put(json.dumps(data), **kwargs)
    if 'http_status' not in res or res['http_status'] != 200:
        return base_common.msg.error('Cannot handle forgot password')

    h = res['h']

    message = _get_email_message(request, h)

    # SAVE EMAILS FOR SENDING
    rh1 = BaseAPIRequestHandler()
    rh1.set_argument('sender', support_mail)
    rh1.set_argument('receiver', newusername)
    rh1.set_argument('message', message)
    kwargs['request_handler'] = rh1
    res = base_api.mail_api.save_mail.do_put(support_mail, newusername, message, **kwargs)
    if 'http_status' not in res or res['http_status'] != 204:
        return base_common.msg.error(msgs.CANNOT_SAVE_MESSAGE)

    message2 = _get_email_warning(dbuser.username, newusername)

    rh2 = BaseAPIRequestHandler()
    rh2.set_argument('sender', support_mail)
    rh2.set_argument('receiver', dbuser.username)
    rh2.set_argument('message', message2)
    kwargs['request_handler'] = rh2
    res = base_api.mail_api.save_mail.do_put(support_mail, dbuser.username, message2, **kwargs)
    if 'http_status' not in res or res['http_status'] != 204:
        return base_common.msg.error(msgs.CANNOT_SAVE_MESSAGE)

    return base_common.msg.post_ok(msgs.CHANGE_USERNAME_REQUEST)

