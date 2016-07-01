# -*- coding: utf-8 -*-

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
from base_common.dbacommon import format_password
from base_common.dbacommon import get_db
from base_common.dbacommon import params
from base_common.dbacommon import app_api_method
from base_common.dbacommon import authenticated_call
from base_common.dbatokens import get_user_by_token
from base_svc.comm import BaseAPIRequestHandler
import base_api.users.changing_username
from base_common.app_hooks import change_username_hook
from base_common.dbacommon import check_user_registered


name = "Change username"
location = "user/username/change"
request_timeout = 10


@authenticated_call()
@app_api_method(
    method='POST',
    api_return=[(200, 'OK'), (404, '')]
)
@params(
    {'arg': 'username', 'type': 'e-mail', 'required': True, 'description': 'users new username'},
    {'arg': 'password', 'type': str, 'required': True, 'description': 'users password'},
    {'arg': 'redirect_url', 'type': str, 'required': True,
     'description': 'successfully changed username redirection url'},
)
def do_post(newusername, password, redirect_url, **kwargs):
    """
    Change username
    """

    _db = get_db()
    dbc = _db.cursor()

    if check_user_registered(dbc, newusername):
        return base_common.msg.error(msgs.USERNAME_ALREADY_TAKEN)

    tk = kwargs['auth_token']

    dbuser = get_user_by_token(_db, tk)

    if not check_password(dbuser.password, dbuser.username, password):
        log.critical('Wrong users password: {}'.format(password))
        return base_common.msg.error(msgs.WRONG_PASSWORD)

    passwd = format_password(newusername, password)

    # SAVE HASH FOR USERNAME CHANGE
    rh = BaseAPIRequestHandler()
    # encryptuj pass, successfully landing page
    data = {'cmd': 'change_username', 'newusername': newusername, 'id_user': dbuser.id_user,
            'password': passwd, 'redirect_url': redirect_url}
    rh.set_argument('data', json.dumps(data, ensure_ascii=False))
    kwargs['request_handler'] = rh
    res = base_api.hash2params.save_hash.do_put(json.dumps(data, ensure_ascii=False), **kwargs)
    if 'http_status' not in res or res['http_status'] != 200:
        return base_common.msg.error('Cannot handle forgot password')

    h = res['h']

    if not change_username_hook(h, newusername, dbuser, **kwargs):
        log.critical('Error finishing username change process')
        return base_common.msg.error(msgs.ERROR_CHANGE_USERNAME)

    return base_common.msg.post_ok(msgs.CHANGE_USERNAME_REQUEST)

