"""
Change user's username
:description:
user confirm username change
"""

import base_common.msg
import base_api.hash2params.save_hash
from base_lookup import api_messages as msgs
from base_common.dbacommon import format_password
from base_common.dbacommon import get_db
from base_common.dbacommon import params
from base_common.dbacommon import app_api_method
from base_svc.comm import BaseAPIRequestHandler
from base_config.service import support_mail
from base_common.dbacommon import get_url_token
from MySQLdb import IntegrityError


name = "Changing username"
location = "user/username/changing/.*"
request_timeout = 10


def _get_email_message():
    """
    Create email message
    :return:  message text as string
    """

    m = 'Dear,<br/> Your username has been updated!<br/>Thank You!'
    return m


@app_api_method(method='GET')
def do_get(request, *args, **kwargs):
    """
    Change password
    :return:  200, OK
    :return:  404
    """

    log = request.log
    _db = get_db()
    dbc = _db.cursor()

    h2p = get_url_token(request, log)
    if not h2p or len(h2p) < 64:
        log.critical('Wrong or expired token {}'.format(h2p))
        return base_common.msg.error(msgs.WRONG_OR_EXPIRED_TOKEN)

    rh = BaseAPIRequestHandler(log)
    rh.set_argument('hash', h2p)
    rh.r_ip = request.r_ip
    res = base_api.hash2params.retrieve_hash.do_get(rh)
    if 'http_status' not in res or res['http_status'] != 200:
        return base_common.msg.error(msgs.PASSWORD_TOKEN_EXPIRED)

    try:
        user_id = res['user_id']
        newusername = res['newusername']
        password = res['password']
    except KeyError as e:
        log.critical('Missing hash parameter: {}'.format(e))
        return base_common.msg.error(msgs.TOKEN_MISSING_ARGUMENT)

    q = '''select username from users where id = '{}' '''.format(user_id)

    try:
        dbc.execute(q)
    except IntegrityError as e:
        log.critical('Error fetching user: {}'.format(e))
        return base_common.msg.error(msgs.USER_NOT_FOUND)

    if dbc.rowcount != 1:
        log.critical('Users found {}'.format(dbc.rowcount))
        return base_common.msg.error(msgs.USER_NOT_FOUND)

    dbu = dbc.fetchone()

    passwd = format_password(newusername, password);

    q1 = '''update users set username = '{}', password = '{}' where id = '{}' '''.format(newusername, passwd, user_id)

    try:
        dbc.execute(q1)
    except IntegrityError as e:
        log.critical('Error updating user: {}'.format(e))
        return base_common.msg.error(msgs.USER_UPDATE_ERROR)

    _db.commit()

    message = _get_email_message()

    # SAVE EMAILS FOR SENDING
    rh1 = BaseAPIRequestHandler(log)
    rh1.set_argument('sender', support_mail)
    rh1.set_argument('receiver', newusername)
    rh1.set_argument('message', message)
    res = base_api.mail_api.save_mail.do_put(rh1)
    if 'http_status' not in res or res['http_status'] != 204:
        return base_common.msg.error(msgs.CANNOT_SAVE_MESSAGE)

    return base_common.msg.post_ok(msgs.USER_NAME_CHANGED)

