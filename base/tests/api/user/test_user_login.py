# coding: utf-8

import json
import urllib
from base.tests.helpers.testing import TestBase
import base.application.lookup.responses as msgs


class TestUserLogin(TestBase):

    def test_login(self):

        self._register('user@test.loc', '123')

        _b = {
            'username': 'user@test.loc',
            'password': '123'
        }

        body = urllib.parse.urlencode(_b)
        res = self.fetch('/login', method='POST', body=body)

        self.assertEqual(res.code, 200)
        res = res.body.decode('utf-8')
        res = json.loads(res)

        self.assertIn('token', res)
        self.assertIn('token_type', res)

    def test_login_with_non_existent_username(self):

        self._register('user@test.loc', '123')

        _b = {
            'username': 'user@test',
            'password': '123'
        }

        body = urllib.parse.urlencode(_b)
        res = self.fetch('/login', method='POST', body=body)

        self.assertEqual(res.code, 400)
        res = res.body.decode('utf-8')
        res = json.loads(res)

        self.assertIn('message', res)
        self.assertEqual(res['message'], msgs.lmap[msgs.WRONG_USERNAME_OR_PASSWORD])

    def test_login_with_wrong_password(self):

        self._register('user@test.loc', '123')

        _b = {
            'username': 'user@test.loc',
            'password': '12'
        }

        body = urllib.parse.urlencode(_b)
        res = self.fetch('/login', method='POST', body=body)

        self.assertEqual(res.code, 400)
        res = res.body.decode('utf-8')
        res = json.loads(res)

        self.assertIn('message', res)
        self.assertEqual(res['message'], msgs.lmap[msgs.WRONG_USERNAME_OR_PASSWORD])

