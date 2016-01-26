"""
Save mail for sending
"""

import json
import datetime
import tornado.web
import base_common.msg
from base_lookup import api_messages as msgs
from base_common.dbacommon import app_api_method
from base_svc.comm import BaseAPIRequestHandler
from base_common.dbacommon import get_md2db
from base_common.dbacommon import qu_esc

name = "E-mail Save"
location = "email/message/save"
request_timeout = 10


def get_mail_query(sender, receiver, message):
    n = datetime.datetime.now()
    q = "insert into mail_queue (id, sender, receiver, time_created, message) " \
        "VALUES " \
        "(null, '{}', '{}', '{}', '{}')".format(
            qu_esc(sender),
            qu_esc(receiver),
            str(n),
            qu_esc(message)
        )

    return q


@app_api_method
def do_put(request, *args, **kwargs):
    """
    Save e-mail message
    :param sender: user who sends a mail, string, True
    :param receiver: user who receive a mail, string, True
    :param message: message to send, string, True
    :return:  200, OK
    :return:  404, notice
    """

    log = request.log
    _db = get_md2db()
    dbc = _db.cursor()

    try:
        sender = request.get_argument('sender')
        receiver = request.get_argument('receiver')
        emessage = request.get_argument('message')
    except tornado.web.MissingArgumentError:
        log.critical('Missing argument')
        return base_common.msg.error(msgs.MISSING_REQUEST_ARGUMENT)

    q = get_mail_query(sender, receiver, emessage)
    from MySQLdb import IntegrityError
    try:
        dbc.execute(q)
    except IntegrityError as e:
        log.critical('Inserting mail queue: {}'.format(e))
        return base_common.msg.error(msgs.CANNOT_SAVE_MESSAGE)

    _db.commit()

    return base_common.msg.post_ok()
