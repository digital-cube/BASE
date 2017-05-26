# coding: utf-8

import json
from base.tests.helpers.testing import TestBase
import base.application.lookup.responses as msgs


class TestMailQueue(TestBase):

    def test_save_mail_unauthorized(self):

        _msg = '<h1>this message is a test</h1></br><p>we just need to check if this mail is properly saved</p>'
        _b = {
             'sender': 'user@test.loc',
             'sender_name': 'test user',
             'receiver': 'receiver@test.loc',
             'receiver_name': 'receive user',
             'subject': 'test email subject',
             'message': _msg,
             # 'data': '',
             # 'get_data': '',
        }

        body = json.dumps(_b)
        res = self.fetch('/tools/mail', method='PUT', body=body)

        self.assertEqual(res.code, 403)
        res = res.body.decode('utf-8')
        res = json.loads(res)

        self.assertIn('message', res)
        self.assertEqual(res['message'], msgs.lmap[msgs.UNAUTHORIZED_REQUEST])

    def test_save_mail_without_data_and_get_id(self):

        self._register('user@test.loc', '123')

        _msg = '<h1>this message is a test</h1></br><p>we just need to check if this mail is properly saved</p>'
        _b = {
             'sender': 'user@test.loc',
             'sender_name': 'test user',
             'receiver': 'receiver@test.loc',
             'receiver_name': 'receive user',
             'subject': 'test email subject',
             'message': _msg,
             # 'data': '',
             # 'get_data': '',
        }

        body = json.dumps(_b)
        headers = {'Authorization': self.token}
        res = self.fetch('/tools/mail', method='PUT', body=body, headers=headers)

        self.assertEqual(res.code, 204)
        res = res.body.decode('utf-8')
        self.assertEqual(res, '')

    def test_save_mail_without_data_get_id_sender_name_receiver_name(self):

        self._register('user@test.loc', '123')

        _msg = '<h1>this message is a test</h1></br><p>we just need to check if this mail is properly saved</p>'
        _b = {
            'sender': 'user@test.loc',
            'receiver': 'receiver@test.loc',
            'subject': 'test email subject',
            'message': _msg,
        }

        body = json.dumps(_b)
        headers = {'Authorization': self.token}
        res = self.fetch('/tools/mail', method='PUT', body=body, headers=headers)

        self.assertEqual(res.code, 204)
        res = res.body.decode('utf-8')
        self.assertEqual(res, '')

    def test_save_mail_without_requested_data(self):

        self._register('user@test.loc', '123')

        _msg = '<h1>this message is a test</h1></br><p>we just need to check if this mail is properly saved</p>'
        _b = {
            'receiver': 'receiver@test.loc',
            'subject': 'test email subject',
            'message': _msg,
        }

        body = json.dumps(_b)
        headers = {'Authorization': self.token}
        res = self.fetch('/tools/mail', method='PUT', body=body, headers=headers)

        self.assertEqual(res.code, 400)
        res = res.body.decode('utf-8')
        res = json.loads(res)

        self.assertIn('message', res)
        self.assertEqual(res['message'], msgs.lmap[msgs.MISSING_REQUEST_ARGUMENT])

    def test_save_mail_with_data(self):

        self._register('user@test.loc', '123')

        _msg = '<h1>this message is a test</h1></br><p>we just need to check if this mail is properly saved</p>'
        _b = {
             'sender': 'user@test.loc',
             'sender_name': 'test user',
             'receiver': 'receiver@test.loc',
             'receiver_name': 'receive user',
             'subject': 'test email subject',
             'message': _msg,
             'data': json.dumps({'custom': 'data'})
        }

        body = json.dumps(_b)
        headers = {'Authorization': self.token}
        res = self.fetch('/tools/mail', method='PUT', body=body, headers=headers)

        self.assertEqual(res.code, 204)
        res = res.body.decode('utf-8')
        self.assertEqual(res, '')

    def test_save_mail_with_data_and_get_id(self):

        self._register('user@test.loc', '123')

        _msg = '<h1>this message is a test</h1></br><p>we just need to check if this mail is properly saved</p>'
        _b = {
            'sender': 'user@test.loc',
            'sender_name': 'test user',
            'receiver': 'receiver@test.loc',
            'receiver_name': 'receive user',
            'subject': 'test email subject',
            'message': _msg,
            'data': json.dumps({'custom': 'data'}),
            'get_data': True
        }

        body = json.dumps(_b)
        headers = {'Authorization': self.token}
        res = self.fetch('/tools/mail', method='PUT', body=body, headers=headers)

        self.assertEqual(res.code, 200)
        res = res.body.decode('utf-8')
        res = json.loads(res)

        self.assertIn('id_message', res)
        self.assertEqual(res['id_message'], 1)


class TestMailQueueSetOptions(TestBase):

    def _save_mail_queue(self):

        _msg = '<h1>this message is a test</h1></br><p>we just need to check if this mail is properly saved</p>'
        _b = {
            'sender': 'user@test.loc',
            'sender_name': 'test user',
            'receiver': 'receiver@test.loc',
            'receiver_name': 'receive user',
            'subject': 'test email subject',
            'message': _msg,
            # 'data': '',
            'get_data': True,
        }

        body = json.dumps(_b)
        headers = {'Authorization': self.token}
        res = self.fetch('/tools/mail', method='PUT', body=body, headers=headers)

        self.assertEqual(res.code, 200)
        res = res.body.decode('utf-8')
        res = json.loads(res)
        self.assertIn('id_message', res)
        self.id_message = res['id_message']

    def test_save_mail_data(self):

        self._register('user@test.loc', '123')
        self._save_mail_queue()

        _b = {
            'sent': True,
            'data': {'additional': 'additional_data'}
        }
        body = json.dumps(_b)
        headers = {'Authorization': self.token}
        res = self.fetch('/tools/mail/{}'.format(self.id_message), method='PATCH', body=body, headers=headers)

        self.assertEqual(res.code, 204)
        res = res.body.decode('utf-8')
        self.assertEqual(res, '')

    def test_save_mail_data_with_non_existing_id(self):

        self._register('user@test.loc', '123')
        self._save_mail_queue()

        _b = {
            'sent': True,
            'data': json.dumps({'additional': 'additional_data'})
        }
        body = json.dumps(_b)
        headers = {'Authorization': self.token}
        res = self.fetch('/tools/mail/9999999999', method='PATCH', body=body, headers=headers)

        self.assertEqual(res.code, 400)
        res = res.body.decode('utf-8')
        res = json.loads(res)

        self.assertIn('message', res)
        self.assertEqual(res['message'], msgs.lmap[msgs.MESSAGE_NOT_FOUND])


class TestMailQueueGet(TestBase):

    def _save_mail_queue(self):

        _msg = '<h1>this message is a test</h1></br><p>we just need to check if this mail is properly saved</p>'
        _b = {
            'sender': 'user@test.loc',
            'sender_name': 'test user',
            'receiver': 'receiver@test.loc',
            'receiver_name': 'receive user',
            'subject': 'test email subject',
            'message': _msg,
            # 'data': '',
            'get_data': True,
        }

        body = json.dumps(_b)
        headers = {'Authorization': self.token}
        res = self.fetch('/tools/mail', method='PUT', body=body, headers=headers)

        self.assertEqual(res.code, 200)
        res = res.body.decode('utf-8')
        res = json.loads(res)
        self.assertIn('id_message', res)
        self.id_message = res['id_message']

    def test_get_mail_data(self):

        self._register('user@test.loc', '123')
        self._save_mail_queue()

        headers = {'Authorization': self.token}
        res = self.fetch('/tools/mail/{}'.format(self.id_message), method='GET', body=None, headers=headers)

        self.assertEqual(res.code, 200)
        res = res.body.decode('utf-8')
        res = json.loads(res)
        self.assertIn('sender', res)
        self.assertEqual(res['sender'], 'user@test.loc')
        self.assertIn('sender_name', res)
        self.assertEqual(res['sender_name'], 'test user')
        self.assertIn('receiver', res)
        self.assertEqual(res['receiver'], 'receiver@test.loc')
        self.assertIn('receiver_name', res)
        self.assertEqual(res['receiver_name'], 'receive user')
        self.assertIn('subject', res)
        self.assertEqual(res['subject'], 'test email subject')

    def test_get_mail_data_with_non_existing_id(self):

        self._register('user@test.loc', '123')
        self._save_mail_queue()

        headers = {'Authorization': self.token}
        res = self.fetch('/tools/mail/9999999999', method='GET', body=None, headers=headers)

        self.assertEqual(res.code, 400)
        res = res.body.decode('utf-8')
        res = json.loads(res)

        self.assertIn('message', res)
        self.assertEqual(res['message'], msgs.lmap[msgs.MESSAGE_NOT_FOUND])
