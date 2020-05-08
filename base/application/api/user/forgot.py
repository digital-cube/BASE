# coding= utf-8

import json
import tornado.gen
import tornado.concurrent

import base.application.lookup.responses as msgs
from base.application.components import Base
from base.application.components import api
from base.application.components import params
from base.common.utils import log


@api(
    URI='/user/forgot',
    PREFIX=False,
    SPECIFICATION_PATH='User')
class Forgot(Base):

    @params(
        {'name': 'username', 'type': 'e-mail', 'required': True,  'doc': "user's username"},
        {'name': 'data', 'type': json, 'required': False,  'doc': "request additional data"},
    )
    def put(self, username, data):
        """Start user forgot password process"""

        import base.common.orm
        AuthUser = base.common.orm.get_orm_model('auth_users')
        with base.common.orm.orm_session() as _session:

            _q = _session.query(AuthUser).filter(AuthUser.username == username)

            if _q.count() == 0:
                log.warning('Non existing user {} request forgot password'.format(username))
                return self.error(msgs.USER_NOT_FOUND)

            user = _q.one()

            from base.application.api_hooks import api_hooks
            if not api_hooks.forgot_password(user, data):
                return self.error(msgs.FORGOT_REQUEST_ERROR)

        return self.ok()

    @params(
        {'name': 'username', 'type': 'e-mail', 'required': True,  'doc': "user's username"},
        {'name': 'data', 'type': json, 'required': False,  'doc': "request additional data"},
    )
    @tornado.gen.coroutine
    def post(self, username, data):
        """Start user forgot password process and send an email"""

        import tornado.concurrent
        executor = tornado.concurrent.futures.ThreadPoolExecutor(max_workers=20)

        from base.application.api_hooks import api_hooks
        save_forgot_request = yield executor.submit(api_hooks.find_user_and_forgot_password, username, data)
        if not save_forgot_request:
            return self.error(msgs.FORGOT_REQUEST_ERROR)

        saved_mail = yield executor.submit(api_hooks.get_email_by_id, save_forgot_request)
        if not saved_mail:
            return self.error(msgs.FORGOT_REQUEST_ERROR)

        sent_mail_response = yield api_hooks.send_mail_from_queue(
            saved_mail['sender'],
            saved_mail['sender_name'],
            saved_mail['receiver'],
            saved_mail['receiver_name'],
            saved_mail['subject'],
            saved_mail['message'],
            saved_mail['data'],
            save_forgot_request)
        if 'status' not in sent_mail_response or not sent_mail_response['status']:
            return self.error('Error send mail for fogot password')

        update_mail_response = yield executor.submit(api_hooks.update_mail_status, save_forgot_request,
                                                     sent_mail_response)
        if not update_mail_response:
            return self.error('Error update mail for forgot password')

        return self.ok({'working': save_forgot_request})
