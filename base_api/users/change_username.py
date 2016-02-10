"""
User change email
:description:
user change the username (email)
"""

import json
import tornado.web
import base_common.msg
import base_api.hash2params.save_hash
from base_lookup import api_messages as msgs
from base_common.dbacommon import check_password
from base_common.dbacommon import qu_esc
from base_common.dbacommon import get_db
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


@authenticated_call
@app_api_method
def do_post(request, *args, **kwargs):
    """
    Change password
    :param username: users new username, string, True
    :param password: users password, string, True
    :return:  200, OK
    :return:  404
    """

    log = request.log
    _db = get_db()
    dbc = _db.cursor()

    try:
        newusername = request.get_argument('username')
        password = request.get_argument('password')
    except tornado.web.MissingArgumentError:
        log.critical('Missing argument password')
        return base_common.msg.error(msgs.MISSING_REQUEST_ARGUMENT)

    tk = request.auth_token
    # u_n, u_p, u_i = get_user_by_token(dbc, tk, log)
    dbuser = get_user_by_token(dbc, tk, log)
    newusername = qu_esc(newusername)
    password = qu_esc(password)

    if not check_password(dbuser.password, dbuser.username, password):
        log.critical('Wrong users password: {}'.format(password))
        return base_common.msg.error(msgs.WRONG_PASSWORD)

    # SAVE HASH FOR USERNAME CHANGE
    rh = BaseAPIRequestHandler(log)
    data = {'cmd': 'change_username', 'newusername': newusername, 'user_id': dbuser.user_id, 'password': password}
    rh.set_argument('data', json.dumps(data))
    res = base_api.hash2params.save_hash.do_put(rh)
    if 'http_status' not in res or res['http_status'] != 200:
        return base_common.msg.error('Cannot handle forgot password')

    h = res['h']

    message = _get_email_message(request, h)

    # SAVE EMAILS FOR SENDING
    rh1 = BaseAPIRequestHandler(log)
    rh1.set_argument('sender', support_mail)
    rh1.set_argument('receiver', newusername)
    rh1.set_argument('message', message)
    res = base_api.mail_api.save_mail.do_put(rh1)
    if 'http_status' not in res or res['http_status'] != 204:
        return base_common.msg.error(msgs.CANNOT_SAVE_MESSAGE)

    message2 = _get_email_warning(dbuser.username, newusername)

    rh2 = BaseAPIRequestHandler(log)
    rh2.set_argument('sender', support_mail)
    rh2.set_argument('receiver', dbuser.username)
    rh2.set_argument('message', message2)
    res = base_api.mail_api.save_mail.do_put(rh2)
    if 'http_status' not in res or res['http_status'] != 204:
        return base_common.msg.error(msgs.CANNOT_SAVE_MESSAGE)

    return base_common.msg.post_ok(msgs.CHANGE_USERNAME_REQUEST)

