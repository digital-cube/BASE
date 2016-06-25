"""
Change user's username
:description:
user confirm username change
"""

import base_common.msg
import base_api.hash2params.save_hash
import base_api.hash2params.retrieve_hash
from base_config.service import log
from base_lookup import api_messages as msgs
from base_common.dbacommon import get_db
from base_common.dbacommon import app_api_method
from base_common.dbacommon import params
from base_svc.comm import BaseAPIRequestHandler
from base_common.dbacommon import get_first_param_uri
from MySQLdb import IntegrityError
from base_common.app_hooks import change_username_success_hook


name = "Changing username"
location = "user/username/changing.*"
request_timeout = 10


@app_api_method(
    method='GET',
    api_return=[(200, 'OK'), (404, '')]
)
@params(
    {'arg': 'hash', 'type': str, 'required': False, 'description': 'hash which refer to users credentials'},
    {'arg': 'redirect', 'type': bool, 'required': False, 'default': True,
     'description': 'redirect, or not, to another address'}
)
def do_get(hash2param, redirect, **kwargs):
    """
    Change username
    """

    _db = get_db()
    dbc = _db.cursor()
    request = kwargs['request_handler']

    if hash2param:
        h2p = hash2param
    else:
        h2p = get_first_param_uri(request)

    if not h2p:
        log.critical('Wrong or expired token {}'.format(h2p))
        return base_common.msg.error(msgs.WRONG_OR_EXPIRED_TOKEN)

    rh = BaseAPIRequestHandler()
    rh.set_argument('hash', h2p)
    kwargs['request_handler'] = rh

    res = base_api.hash2params.retrieve_hash.do_get(h2p, False, **kwargs)
    if 'http_status' not in res or res['http_status'] != 200:
        return base_common.msg.error(msgs.PASSWORD_TOKEN_EXPIRED)

    try:
        id_user = res['id_user']
        newusername = res['newusername']
        password = res['password']
    except KeyError as e:
        log.critical('Missing hash parameter: {}'.format(e))
        return base_common.msg.error(msgs.TOKEN_MISSING_ARGUMENT)

    q = '''select username from users where id = '{}' '''.format(id_user)

    try:
        dbc.execute(q)
    except IntegrityError as e:
        log.critical('Error fetching user: {}'.format(e))
        return base_common.msg.error(msgs.USER_NOT_FOUND)

    if dbc.rowcount != 1:
        log.critical('Users found {}'.format(dbc.rowcount))
        return base_common.msg.error(msgs.USER_NOT_FOUND)

    q1 = '''update users set username = '{}', password = '{}' where id = '{}' '''.format(newusername, password, id_user)

    try:
        dbc.execute(q1)
    except IntegrityError as e:
        log.critical('Error updating user: {}'.format(e))
        return base_common.msg.error(msgs.USER_UPDATE_ERROR)

    _db.commit()

    if not change_username_success_hook(newusername, **kwargs):
        log.critical('Error sending info message')
        return base_common.msg.error(msgs.CANNOT_SAVE_MESSAGE)

    if redirect:
        if 'redirect_url' not in res:
            log.critical('Missing redirect url in saved hash')
            return base_common.msg.error(msgs.MISSING_REDIRECTION_URL)

        return base_common.msg.post_ok({'redirect': True, 'redirect_url': res['redirect_url']})

    return base_common.msg.post_ok(msgs.USER_NAME_CHANGED)

