# -*- coding: utf-8 -*-

"""
Save mail for sending
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

name = "E-mail Save"
location = "email/message/save"
request_timeout = 10


def get_mail_query(sender, sender_name, receiver, receiver_name, subject, message, data):
    n = datetime.datetime.now()
    q = "insert into mail_queue (id, sender, sender_name, receiver, receiver_name, time_created, subject, message, data) " \
        "VALUES " \
        "(null, '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')".format(
            sender,
            sender_name,
            receiver,
            receiver_name,
            str(n),
            subject,
            message,
            data if data else ''
        )

    return q


@app_api_method(
    method='PUT',
    expose=False,
    api_return=[(200, 'OK'), (404, 'notice')]
)
@params(
    {'arg': 'sender', 'type': str, 'required': True, 'description': 'user who sends a mail'},
    {'arg': 'sender_name', 'type': str, 'required': False, 'description': 'name of the sender'},
    {'arg': 'receiver', 'type': str, 'required': True, 'description': 'user who receive a mail'},
    {'arg': 'receiver_name', 'type': str, 'required': False, 'description': 'user who receive a mail'},
    {'arg': 'subject', 'type': str, 'required': True, 'description': 'subject of the message'},
    {'arg': 'message', 'type': str, 'required': True, 'description': 'message to send'},
    {'arg': '_get_id', 'type': bool, 'required': False, 'default': False, 'description': 'test flag'},
    {'arg': 'data', 'type': json, 'required': False, 'description': 'additional email data'},
)
def do_put(sender, sender_name, receiver, receiver_name, subject, emessage, _get_id, data, **kwargs):
    """
    Save e-mail message
    """
    return save_email(sender, sender_name, receiver, receiver_name, subject, emessage, _get_id, data)


def save_email(sender, sender_name, receiver, receiver_name, subject, emessage, _get_id, data, **kwargs):

    _db = get_db()
    dbc = _db.cursor()
    rdb = get_redis_db()

    if sender_name is None:
        sender_name = sender
    if receiver_name is None:
        receiver_name = receiver

    q = get_mail_query(sender, sender_name, receiver, receiver_name, subject, emessage, data)
    from MySQLdb import IntegrityError
    try:
        dbc.execute(q)
    except IntegrityError as e:
        log.critical('Inserting mail queue: {}'.format(e))
        return base_common.msg.error(msgs.CANNOT_SAVE_MESSAGE)

    _db.commit()
    m_id = dbc.lastrowid

    r_data = {
        'id': m_id,
        'sender': sender,
        'sender_name': sender_name,
        'receiver': receiver,
        'receiver_name': receiver_name,
        'subject': subject,
        'message': emessage
    }

    r_data = json.dumps(r_data, ensure_ascii=False)

    rdb.lpush(MAIL_CHANNEL, r_data)

    if _get_id:
        return base_common.msg.post_ok({'message_id': m_id})

    return base_common.msg.post_ok()
