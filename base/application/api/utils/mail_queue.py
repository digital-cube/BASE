# coding= utf-8

import json
import base.common.orm
from base.common.utils import log
from base.application.components import Base
from base.application.components import api
from base.application.components import params
from base.application.components import authenticated

import base.application.lookup.responses as msgs


@authenticated()
@api(
    URI='/mail',
    PREFIX=False)
class MailQueue(Base):

    @params(
        {'name': 'id_message', 'type': int, 'required': True,  'doc': 'message id'},
    )
    def get(self, id_message):

        return self.ok()

    @params(
        {'name': 'sender', 'type': str, 'required': True,  'doc': 'message sender email address'},
        {'name': 'sender_name', 'type': str, 'required': False,  'doc': 'sender display name'},
        {'name': 'receiver', 'type': str, 'required': True,  'doc': 'message receiver email address'},
        {'name': 'receiver_name', 'type': str, 'required': False,  'doc': 'receiver display name'},
        {'name': 'subject', 'type': str, 'required': True,  'doc': 'message subject'},
        {'name': 'message', 'type': str, 'required': True,  'doc': 'message body'},
        {'name': 'data', 'type': json, 'required': False,  'doc': 'message additional data'},
        {'name': 'get_data', 'type': bool, 'required': False,  'doc': 'will retrieve message data'},
    )
    def put(self, sender, sender_name, receiver, receiver_name, subject, message, data, get_data):

        log.info('Save message for {} by {}'.format(receiver, sender))
        from base.application.api import api_hooks

        try:
            id_message = api_hooks.save_mail_queue(sender, sender_name, receiver, receiver_name, subject, message, data)
        except:
            log.critical('Error save mail queue')
            return self.error(msgs.SAVE_MAIL_QUEUE_ERROR)

        if get_data:
            return self.ok({'id_message': id_message})

        return self.ok()

    @params(
        {'name': 'id_message', 'type': int, 'required': True,  'doc': 'message id'},
    )
    def patch(self, id_message):

        return self.ok()

