# coding: utf-8

import json
import urllib
from base.tests.helpers.testing import TestBase
import base.application.lookup.responses as msgs


class TestOptions(TestBase):

    def _register(self):

        _b = {
            'username': 'user@test.loc',
            'password': '123',
            'data': {}
        }

        body = urllib.parse.urlencode(_b)
        res = self.fetch('/register', method='POST', body=body)

        self.assertEqual(res.code, 200)
        res = res.body.decode('utf-8')
        res = json.loads(res)

        self.assertIn('token', res)
        self.assertIn('token_type', res)

        self.token = res['token']

    def _set_option(self):

        _b = {
            'value': '123'
        }
        body = urllib.parse.urlencode(_b)
        headers = {'Authorization': self.token}
        res = self.fetch('/option/test_option?value=321', method='PUT', body=body, headers=headers)

        self.assertEqual(res.code, 200)
        res = res.body.decode('utf-8')
        res = json.loads(res)

        self.assertIn('test_option', res)
        self.assertEqual(res['test_option'], '321')

    def test_set_option_unauthorized(self):

        _b = {
            'value': '123'
        }

        body = urllib.parse.urlencode(_b)
        res = self.fetch('/option/test_option', method='PUT', body=body)

        self.assertEqual(res.code, 400)
        res = res.body.decode('utf-8')
        res = json.loads(res)

        self.assertIn('message', res)
        self.assertEqual(res['message'], msgs.lmap[msgs.UNAUTHORIZED_REQUEST])

    def test_set_option(self):

        self._register()

        _b = {
            'value': '123'
        }
        body = urllib.parse.urlencode(_b)
        headers = {'Authorization': self.token}
        res = self.fetch('/option/test_option?value=321', method='PUT', body=body, headers=headers)

        self.assertEqual(res.code, 200)
        res = res.body.decode('utf-8')
        res = json.loads(res)

        self.assertIn('test_option', res)
        self.assertEqual(res['test_option'], '321')

    def test_get_option(self):

        self._register()
        self._set_option()

        headers = {'Authorization': self.token}
        res = self.fetch('/option/test_option', method='GET', headers=headers)

        self.assertEqual(res.code, 200)
        res = res.body.decode('utf-8')
        res = json.loads(res)

        self.assertIn('test_option', res)
        self.assertEqual(res['test_option'], '321')

    def test_get_unexisting_option(self):

        self._register()
        self._set_option()

        headers = {'Authorization': self.token}
        res = self.fetch('/option/test_option_not_exists', method='GET', headers=headers)

        self.assertEqual(res.code, 400)
        res = res.body.decode('utf-8')
        res = json.loads(res)

        self.assertIn('option', res)
        self.assertEqual(res['option'], 'test_option_not_exists')
        self.assertIn('message', res)
        self.assertEqual(res['message'], msgs.lmap[msgs.MISSING_OPTION])