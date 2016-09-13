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
import sys

name = "E-mail Save"
location = "email/message/save"
request_timeout = 10

#
# def get_mail_query(sender, sender_name, receiver, receiver_name, subject, message, data):
#     n = datetime.datetime.now()
#     q = "insert into mail_queue (id, sender, sender_name, receiver, receiver_name, time_created, subject, message, data) " \
#         "VALUES " \
#         "(null, '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')".format(
#             sender,
#             sender_name,
#             receiver,
#             receiver_name,
#             str(n),
#             subject,
#             message,
#             data if data else ''
#         )
#
#     return q


#TODO: ograniciti ga samo na lokal!

@app_api_method(
    method='PUT',

    expose=True,    #TODO da bude expozovan samo na lokalu

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
    res, err, m_id = save_email(sender, sender_name, receiver, receiver_name, subject, emessage, _get_id, data)

    if not res:
        return base_common.msg.error(err)

    if m_id:
        return base_common.msg.ok({'message_id': m_id})

    return base_common.msg.ok()


def save_email(sender, sender_name, receiver, receiver_name, subject, emessage, _get_id, data, db=None, **kwargs):

    if not db:
        _db = get_db()
    else:
        _db = db
    
    dbc = _db.cursor()
    rdb = get_redis_db()

    if sender_name is None:
        sender_name = sender
    if receiver_name is None:
        receiver_name = receiver

    from MySQLdb import IntegrityError
    try:
        dbc.execute('insert into mail_queue (id, sender, sender_name, receiver, receiver_name, time_created, subject, message, data) values (%s,%s,%s,%s,%s,now(),%s,%s,%s)',
                    (None, sender, sender_name, receiver, receiver_name, subject, emessage, data))

        # print (dbc._last_executed)
    except IntegrityError as e:
        log.critical('Inserting mail queue: {}'.format(e))
        return False, msgs.CANNOT_SAVE_MESSAGE, None

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

    from config import send_mail_config

    __SVC_PORT = send_mail_config.SVC_PORT
    rdb.lpush("{} {}".format(MAIL_CHANNEL, __SVC_PORT), r_data)

    if _get_id:
        return True, None, m_id

    return True, None, None
