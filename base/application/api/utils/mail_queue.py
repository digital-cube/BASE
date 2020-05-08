# coding= utf-8

import json
import tornado.gen
import tornado.concurrent

import base.application.lookup.responses as msgs
import base.common.orm
from base.application.components import Base
from base.application.components import api
from base.application.components import authenticated
from base.application.components import params
from base.application.helpers.exceptions import MailQueueError
from base.common.utils import log


@authenticated()
@api(
    URI='/tools/mail',
    PREFIX=False)
class MailQueue(Base):

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
        """
        Save message to queue
        This should be changed for post on any new implementation
        """

        log.info('Save message for {} by {}'.format(receiver, sender))
        from base.application.api_hooks import api_hooks

        try:
            id_message = api_hooks.save_mail_queue(sender, sender_name, receiver, receiver_name, subject, message, data)
        except MailQueueError as e:
            log.critical('Error save mail queue: {}'.format(e))
            return self.error(msgs.SAVE_MAIL_QUEUE_ERROR)

        if get_data:
            return self.ok({'id_message': id_message})

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
    @tornado.gen.coroutine
    def post(self, sender, sender_name, receiver, receiver_name, subject, message, data, get_data):
        """Save message to queue and send message over configured client"""

        log.info('Send message for {} by {}'.format(receiver, sender))

        executor = tornado.concurrent.futures.ThreadPoolExecutor(max_workers=20)

        from base.application.api_hooks import api_hooks
        save_mail_response = yield executor.submit(api_hooks.save_mail_queue, sender, sender_name, receiver, receiver_name, subject, message, data, False)
        if not save_mail_response:
            return self.error('Error save mail queue')

        sent_mail_response = yield api_hooks.send_mail_from_queue(sender, sender_name, receiver, receiver_name, subject, message, data, save_mail_response)
        if 'status' not in sent_mail_response or not sent_mail_response['status']:
            return self.error('Error send mail from queue')

        update_mail_response = yield executor.submit(api_hooks.update_mail_status, save_mail_response, sent_mail_response)
        if not update_mail_response:
            return self.error('Error update mail queue')

        if get_data:
            return self.ok({'id_message': save_mail_response})

        return self.ok()


@authenticated()
@api(
    URI='/tools/mail/:id_message',
    PREFIX=False,
    SPECIFICATION_PATH='MailQueue')
class MailQueueHandle(Base):

    @params(
        {'name': 'id_message', 'type': int, 'required': True,  'doc': 'message id'},
        {'name': 'sent', 'type': bool, 'required': False,  'doc': 'message is sent'},
        {'name': 'data', 'type': 'json', 'required': False,  'doc': 'message data to update'},
    )
    def patch(self, id_message, sent, data):
        """Update message status and data"""

        MQ = base.common.orm.get_orm_model('mail_queue')

        q = self.orm_session.query(MQ).filter(MQ.id == id_message)

        if q.count() == 0:
            log.warning('No message with id {} found'.format(id_message))
            return self.error(msgs.MESSAGE_NOT_FOUND)

        msg = q.one()
        _commit = False
        if sent is not None:
            msg.sent = sent
            _commit = True

        if data is not None:

            try:
                msg_data = json.loads(msg.data)
            except json.JSONDecodeError as e:
                log.error('Error loading message {} data {}: {}'.format(id_message, msg.data, e))
                msg_data = {}
            except TypeError as e:
                log.warning('Message {} missing data {}: {}'.format(id_message, msg.data, e))
                msg_data = {}

            msg_data.update(data)
            msg.data = json.dumps(msg_data)
            _commit = True

        if _commit:
            self.orm_session.commit()

        return self.ok()

    @params(
        {'name': 'id_message', 'type': int, 'required': True,  'doc': 'message id'},
    )
    def get(self, id_message):
        """Get message"""

        from base.application.api_hooks import api_hooks

        try:
            _message_data = api_hooks.get_mail_from_queue(id_message)
        except MailQueueError as e:
            log.critical('Error save mail queue: {}'.format(e))
            return self.error(msgs.SAVE_MAIL_QUEUE_ERROR)

        if not _message_data:
            return self.error(msgs.MESSAGE_NOT_FOUND)

        return self.ok(_message_data)

