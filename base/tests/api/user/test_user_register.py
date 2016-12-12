# coding: utf-8

import json
import urllib
from base.tests.helpers.testing import TestBase
import base.application.lookup.responses as msgs


class TestUserRegister(TestBase):

    def test_register(self):

        _b = {
            'username': 'user@test.loc',
            'password': '123',
            'data': {}
        }

        body = urllib.parse.urlencode(_b)
        res = self.fetch('/register', method='POST', body=body)

        self.assertEqual(res.code, 200)
        res = res.body.decode('utf-8')

        self.assertIn('token', res)
        self.assertIn('token_type', res)
        self.assertTrue(True)

    def test_register_with_same_username(self):

        _b = {
            'username': 'user@this.loc',
            'password': '123',
            'data': {}
        }
        body = urllib.parse.urlencode(_b)
        res = self.fetch('/register', method='POST', body=body)
        self.assertEqual(res.code, 200)
        res = res.body.decode('utf-8')
        self.assertIn('token', res)
        self.assertIn('token_type', res)

        res2 = self.fetch('/register', method='POST', body=body)
        self.assertEqual(res2.code, 400)
        res2 = res2.body.decode('utf-8')
        res2 = json.loads(res2)
        self.assertIn('message', res2)
        self.assertEqual(res2['message'], msgs.lmap[msgs.USERNAME_ALREADY_TAKEN])

        self.assertTrue(True)

    def test_register_with_wrong_username(self):

        _b = {
            'username': 'user',
            'password': '123',
            'data': {}
        }
        body = urllib.parse.urlencode(_b)
        res = self.fetch('/register', method='POST', body=body)
        self.assertEqual(res.code, 400)
        res = res.body.decode('utf-8')
        res = json.loads(res)
        self.assertIn('message', res)
        self.assertEqual(res['message'], msgs.lmap[msgs.INVALID_REQUEST_ARGUMENT])

        self.assertTrue(True)
