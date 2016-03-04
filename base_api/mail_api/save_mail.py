"""
Save mail for sending
"""

import datetime
import base_common.msg
from base_lookup import api_messages as msgs
from base_common.dbacommon import params
from base_common.dbacommon import app_api_method
from base_common.dbacommon import get_db

name = "E-mail Save"
location = "email/message/save"
request_timeout = 10


def get_mail_query(sender, receiver, message):
    n = datetime.datetime.now()
    q = "insert into mail_queue (id, sender, receiver, time_created, message) " \
        "VALUES " \
        "(null, '{}', '{}', '{}', '{}')".format(
            sender,
            receiver,
            str(n),
            message
        )

    return q


@app_api_method(
    method='PUT',
    expose=False,
    api_return=[(200, 'OK'), (404, 'notice')]
)
@params(
    {'arg': 'sender', 'type': str, 'required': True, 'description': 'user who sends a mail'},
    {'arg': 'receiver', 'type': str, 'required': True, 'description': 'user who receive a mail'},
    {'arg': 'message', 'type': str, 'required': True, 'description': 'message to send'},
    {'arg': '_get_id', 'type': bool, 'required': False, 'default': False, 'description': 'test flag'},
)
def do_put(request, *args, **kwargs):
    """
    Save e-mail message
    """

    log = request.log
    _db = get_db()
    dbc = _db.cursor()

    sender, receiver, emessage, _get_id = args

    q = get_mail_query(sender, receiver, emessage)
    from MySQLdb import IntegrityError
    try:
        dbc.execute(q)
    except IntegrityError as e:
        log.critical('Inserting mail queue: {}'.format(e))
        return base_common.msg.error(msgs.CANNOT_SAVE_MESSAGE)

    _db.commit()

    if _get_id:

        m_id = dbc.lastrowid
        return base_common.msg.post_ok({'message_id': m_id})

    return base_common.msg.post_ok()
