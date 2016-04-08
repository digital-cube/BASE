"""
Mail Sent
"""

import json
import datetime
import base_common.msg
from base_lookup import api_messages as msgs
from base_config.service import log
from base_config.settings import MAIL_CHANNEL
from base_common.dbacommon import params
from base_common.dbacommon import app_api_method
from base_common.dbacommon import get_db
from base_common.dbacommon import get_redis_db

name = "E-mail"
location = "email/sent"
request_timeout = 10


def get_mail_query(id_msg, msg_datetime):

    q = '''UPDATE mail_queue set sent = true, time_sent = '{}' WHERE id = {} '''.format(str(msg_datetime), id_msg)

    return q


@app_api_method(
    method='PATCH',
    api_return=[(200, 'OK'), (404, 'notice')]
)
@params(
    {'arg': 'id_message', 'type': int, 'required': True, 'description': 'message id'},
    {'arg': 'sent_time', 'type': str, 'required': True, 'description': 'message sent time'},
)
def set_mail_sent(id_message, message_sent_time, **kwargs):
    """
    Set e-mail sent
    """

    _db = get_db()
    dbc = _db.cursor()

    q = get_mail_query(id_message, message_sent_time)
    from MySQLdb import IntegrityError
    try:
        dbc.execute(q)
    except IntegrityError as e:
        log.critical('Update mail queue: {}'.format(e))
        return base_common.msg.error(msgs.ERROR_UPDATE_MESSAGE)

    _db.commit()

    return base_common.msg.patch_ok()
