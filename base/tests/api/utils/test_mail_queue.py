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
        res = self.fetch('/mail', method='PUT', body=body)

        self.assertEqual(res.code, 400)
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
        res = self.fetch('/mail', method='PUT', body=body, headers=headers)

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
        res = self.fetch('/mail', method='PUT', body=body, headers=headers)

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
        res = self.fetch('/mail', method='PUT', body=body, headers=headers)

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
        res = self.fetch('/mail', method='PUT', body=body, headers=headers)

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
        res = self.fetch('/mail', method='PUT', body=body, headers=headers)

        self.assertEqual(res.code, 200)
        res = res.body.decode('utf-8')
        res = json.loads(res)

        self.assertIn('id_message', res)
        self.assertEqual(res['id_message'], 1)

