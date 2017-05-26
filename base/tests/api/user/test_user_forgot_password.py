# coding: utf-8

import json
import urllib
from base.tests.helpers.testing import TestBase
import base.application.lookup.responses as msgs


class TestUserForgot(TestBase):

    def test_unknown_user(self):

        self._register('user@test.loc', '123')

        _b = {
            'username': 'user1@test.loc',
            'data': {'additional': 'additional_data'}
        }

        body = json.dumps(_b)
        res = self.fetch('/user/forgot', method='PUT', body=body)

        self.assertEqual(res.code, 400)
        res = res.body.decode('utf-8')
        res = json.loads(res)
        self.assertIn('message', res)
        self.assertEqual(res['message'], msgs.lmap[msgs.USER_NOT_FOUND])

    def test_forgot_password(self):

        self._register('user@test.loc', '123')

        _b = {
            'username': 'user@test.loc',
            'data': {'additional': 'additional_data'}
        }

        body = json.dumps(_b)
        res = self.fetch('/user/forgot', method='PUT', body=body)

        self.assertEqual(res.code, 204)
        res = res.body.decode('utf-8')
        self.assertEqual(res, '')

