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

        # self.assertEqual(res.code, 200)
        # res = res.body.decode('utf-8')
        # res = json.loads(res)
        #
        # self.assertIn('token', res)
        # self.assertIn('token_type', res)

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

        # self.assertEqual(res.code, 200)
        # res = res.body.decode('utf-8')
        # res = json.loads(res)
        #
        # self.assertIn('token', res)
        # self.assertIn('token_type', res)

    # def test_login_with_non_existent_username(self):
    #
    #     self._register('user@test.loc', '123')
    #
    #     _b = {
    #         'username': 'user@test',
    #         'data': {'additional': 'additional_data'}
    #     }
    #
    #     body = json.dumps(_b)
    #     res = self.fetch('/user/login', method='POST', body=body)
    #
    #     self.assertEqual(res.code, 400)
    #     res = res.body.decode('utf-8')
    #     res = json.loads(res)
    #
    #     self.assertIn('message', res)
    #     self.assertEqual(res['message'], msgs.lmap[msgs.WRONG_USERNAME_OR_PASSWORD])
    #
    # def test_login_with_wrong_password(self):
    #
    #     self._register('user@test.loc', '123')
    #
    #     _b = {
    #         'username': 'user@test.loc',
    #         'password': '12'
    #     }
    #
    #     body = json.dumps(_b)
    #     res = self.fetch('/user/login', method='POST', body=body)
    #
    #     self.assertEqual(res.code, 400)
    #     res = res.body.decode('utf-8')
    #     res = json.loads(res)
    #
    #     self.assertIn('message', res)
    #     self.assertEqual(res['message'], msgs.lmap[msgs.WRONG_USERNAME_OR_PASSWORD])
    #
    # def test_user_check(self):
    #
    #     self._register('user@test.loc', '123')
    #
    #     _b = {
    #         'username': 'user@test.loc',
    #         'password': '123'
    #     }
    #
    #     body = json.dumps(_b)
    #     res = self.fetch('/user/login', method='POST', body=body)
    #
    #     self.assertEqual(res.code, 200)
    #     res = res.body.decode('utf-8')
    #     res = json.loads(res)
    #
    #     self.assertIn('token', res)
    #     self.assertIn('token_type', res)
    #
    #     token = res['token']
    #
    #     headers = {'Authorization': token}
    #     res = self.fetch('/user/login', method='GET', body=None, headers=headers)
    #
    #     self.assertEqual(res.code, 200)
    #     res = res.body.decode('utf-8')
    #     res = json.loads(res)
    #
    #     self.assertIn('id', res)
    #     self.assertIn('username', res)
    #     self.assertIn('first_name', res)
    #     self.assertIn('last_name', res)
    #
    #     self.assertEqual(res['username'], 'user@test.loc')
    #
    # def test_user_check_error(self):
    #
    #     self._register('user@test.loc', '123')
    #
    #     _b = {
    #         'username': 'user@test.loc',
    #         'password': '123'
    #     }
    #
    #     body = json.dumps(_b)
    #     res = self.fetch('/user/login', method='POST', body=body)
    #
    #     self.assertEqual(res.code, 200)
    #     res = res.body.decode('utf-8')
    #     res = json.loads(res)
    #     self.assertIn('token', res)
    #     self.assertIn('token_type', res)
    #
    #     token = res['token']
    #     headers = {'Authorization': token}
    #
    #     body = json.dumps({})
    #     res = self.fetch('/user/logout', method='POST', body=body, headers=headers)
    #     self.assertEqual(res.code, 204)
    #     self.assertEqual(res.body, b'')
    #
    #     res = self.fetch('/user/login', method='GET', body=None, headers=headers)
    #
    #     self.assertEqual(res.code, 400)
    #     res = res.body.decode('utf-8')
    #     res = json.loads(res)
    #     self.assertIn('message', res)
    #     self.assertEqual(res['message'], msgs.lmap[msgs.UNAUTHORIZED_REQUEST])

