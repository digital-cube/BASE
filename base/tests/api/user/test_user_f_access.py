# coding: utf-8

import copy
import json
from unittest.mock import patch
from base.tests.helpers.testing import TestBase
import base.application.lookup.responses as msgs


FACEBOOK_USER = {
    "email": "test@user.com",
    "id": "xxxx",
    "image": "https://graph.facebook.com/xxx/picture?type=normal",
    "name": "Test User",
    "provider": "facebook",
    "token": "xxx",
    "first_name": "Test",
    "gender": "male",
    "last_name": "User",
    "headers": {'ETag': 'xxxx', 'Strict-Transport-Security': 'max-age=15552000; preload', 'x-fb-trace-id': 'xxxx', 'x-fb-rev': 'xxxx', 'x-app-usage': '{"call_count":11,"total_cputime":0,"total_time":1}', 'Expires': 'Sat, 01 Jan 2000 00:00:00 GMT', 'Content-Type': 'application/json; charset=UTF-8', 'facebook-api-version': 'v2.8', 'Cache-Control': 'private, no-cache, no-store, must-revalidate', 'Pragma': 'no-cache', 'Access-Control-Allow-Origin': '*', 'Vary': 'Accept-Encoding', 'Content-Encoding': 'gzip', 'X-FB-Debug': 'xxxx', 'Date': 'Sat, 01 Jan 2000 00:00:00 GMT', 'Connection': 'keep-alive', 'Content-Length': '130'}
}


def _user_info(self):
    return True


def _user_info_error(self):
    return False


def _log_in_user_error(self):
    return False


def _log_in_user(self):
    return True


def _missing_module():
    return False


def _module_installed():
    return True


_FUSER = {
    "email": "test@user.com",
    "id": "id_of_the_user",
    "image": "https://address.to.the.pic/id",
    "name": "Test User",
    "provider": "facebook",
    "token": "xxx"
}


class TestUserFAccess(TestBase):

    @patch('base.application.api.user.faccess.check_facepy_library_installed', _missing_module)
    def test_f_login_missing_facepy_module(self):

        _b = {
            'user': json.dumps(_FUSER, ensure_ascii=False)
        }

        body = json.dumps(_b)
        res = self.fetch('/user/f-access', method='POST', body=body)

        self.assertEqual(res.code, 400)
        res = res.body.decode('utf-8')
        res = json.loads(res)
        self.assertIn('message', res)
        self.assertEqual(res['message'], msgs.lmap[msgs.FACEBOOK_LIBRARY_NOT_INSTALLED])

    @patch('base.application.api.user.faccess.FAccess.get_user_info', _user_info)
    @patch('base.application.api.user.faccess.FAccess.social_user', FACEBOOK_USER)
    @patch('base.application.api.user.faccess.FAccess.log_user_in', _log_in_user_error)
    def test_f_login_missing_facepy_module2(self):

        _b = {
            'user': json.dumps(_FUSER, ensure_ascii=False)
        }

        body = json.dumps(_b)
        res = self.fetch('/user/f-access', method='POST', body=body)

        self.assertEqual(res.code, 400)
        res = res.body.decode('utf-8')
        res = json.loads(res)
        self.assertIn('message', res)
        self.assertEqual(res['message'], msgs.lmap[msgs.FACEBOOK_LIBRARY_NOT_INSTALLED])

    @patch('base.application.api.user.faccess.check_facepy_library_installed', _module_installed)
    def test_f_login_invalid_facebook_user_sent(self):

        # missing email
        F1 = copy.deepcopy(_FUSER)
        del F1['email']
        _b = {
            'user': json.dumps(F1, ensure_ascii=False)
        }

        body = json.dumps(_b)
        res = self.fetch('/user/f-access', method='POST', body=body)

        self.assertEqual(res.code, 400)
        res = res.body.decode('utf-8')
        res = json.loads(res)
        self.assertIn('message', res)
        self.assertEqual(res['message'], msgs.lmap[msgs.FACEBOOK_USER_INVALID])

        # missing id
        F2 = copy.deepcopy(_FUSER)
        del F2['id']
        _b = {
            'user': json.dumps(F2, ensure_ascii=False)
        }

        body = json.dumps(_b)
        res = self.fetch('/user/f-access', method='POST', body=body)

        self.assertEqual(res.code, 400)
        res = res.body.decode('utf-8')
        res = json.loads(res)
        self.assertIn('message', res)
        self.assertEqual(res['message'], msgs.lmap[msgs.FACEBOOK_USER_INVALID])

        # missing image
        F3 = copy.deepcopy(_FUSER)
        del F3['image']
        _b = {
            'user': json.dumps(F3, ensure_ascii=False)
        }

        body = json.dumps(_b)
        res = self.fetch('/user/f-access', method='POST', body=body)

        self.assertEqual(res.code, 400)
        res = res.body.decode('utf-8')
        res = json.loads(res)
        self.assertIn('message', res)
        self.assertEqual(res['message'], msgs.lmap[msgs.FACEBOOK_USER_INVALID])

        # missing name
        F4 = copy.deepcopy(_FUSER)
        del F4['image']
        _b = {
            'user': json.dumps(F4, ensure_ascii=False)
        }

        body = json.dumps(_b)
        res = self.fetch('/user/f-access', method='POST', body=body)

        self.assertEqual(res.code, 400)
        res = res.body.decode('utf-8')
        res = json.loads(res)
        self.assertIn('message', res)
        self.assertEqual(res['message'], msgs.lmap[msgs.FACEBOOK_USER_INVALID])

        # missing provider
        F5 = copy.deepcopy(_FUSER)
        del F5['provider']
        _b = {
            'user': json.dumps(F5, ensure_ascii=False)
        }

        body = json.dumps(_b)
        res = self.fetch('/user/f-access', method='POST', body=body)

        self.assertEqual(res.code, 400)
        res = res.body.decode('utf-8')
        res = json.loads(res)
        self.assertIn('message', res)
        self.assertEqual(res['message'], msgs.lmap[msgs.FACEBOOK_USER_INVALID])

        # missing token
        F6 = copy.deepcopy(_FUSER)
        del F6['token']
        _b = {
            'user': json.dumps(F6, ensure_ascii=False)
        }

        body = json.dumps(_b)
        res = self.fetch('/user/f-access', method='POST', body=body)

        self.assertEqual(res.code, 400)
        res = res.body.decode('utf-8')
        res = json.loads(res)
        self.assertIn('message', res)
        self.assertEqual(res['message'], msgs.lmap[msgs.FACEBOOK_USER_INVALID])

        # invalid provider
        F7 = copy.deepcopy(_FUSER)
        F7['provider'] = 'invalid provider'
        _b = {
            'user': json.dumps(F7, ensure_ascii=False)
        }

        body = json.dumps(_b)
        res = self.fetch('/user/f-access', method='POST', body=body)

        self.assertEqual(res.code, 400)
        res = res.body.decode('utf-8')
        res = json.loads(res)
        self.assertIn('message', res)
        self.assertEqual(res['message'], msgs.lmap[msgs.FACEBOOK_USER_INVALID])

    @patch('base.application.api.user.faccess.check_facepy_library_installed', _module_installed)
    @patch('base.application.api.user.faccess.FAccess.get_user_info', _user_info_error)
    @patch('base.application.api.user.faccess.FAccess.social_user', FACEBOOK_USER)
    @patch('base.application.api.user.faccess.FAccess.log_user_in', _log_in_user_error)
    def test_f_login_can_not_verify_token(self):

        _b = {
            'user': json.dumps(_FUSER, ensure_ascii=False)
        }

        body = json.dumps(_b)
        res = self.fetch('/user/f-access', method='POST', body=body)

        self.assertEqual(res.code, 400)
        res = res.body.decode('utf-8')
        res = json.loads(res)
        self.assertIn('message', res)
        self.assertEqual(res['message'], msgs.lmap[msgs.ERROR_GET_FACEBOOK_USER])

    @patch('base.application.api.user.faccess.check_facepy_library_installed', _module_installed)
    @patch('base.application.api.user.faccess.FAccess.get_user_info', _user_info)
    @patch('base.application.api.user.faccess.FAccess.social_user', FACEBOOK_USER)
    @patch('base.application.api.user.faccess.FAccess.log_user_in', _log_in_user_error)
    def test_g_access_can_not_register_or_login_user(self):

        _b = {
            'user': json.dumps(_FUSER, ensure_ascii=False)
        }

        body = json.dumps(_b)
        res = self.fetch('/user/f-access', method='POST', body=body)

        self.assertEqual(res.code, 400)
        res = res.body.decode('utf-8')
        res = json.loads(res)
        self.assertIn('message', res)
        self.assertEqual(res['message'], msgs.lmap[msgs.ERROR_AUTHORIZE_FACEBOOK_USER])

    @patch('base.application.api.user.faccess.check_facepy_library_installed', _module_installed)
    @patch('base.application.api.user.faccess.FAccess.get_user_info', _user_info)
    @patch('base.application.api.user.faccess.FAccess.social_user', FACEBOOK_USER)
    def test_f_login(self):

        _b = {
            'user': json.dumps(_FUSER, ensure_ascii=False)
        }

        body = json.dumps(_b)
        res = self.fetch('/user/f-access', method='POST', body=body)

        self.assertEqual(res.code, 200)
        res = res.body.decode('utf-8')
        res = json.loads(res)
        self.assertIn('token', res)
        self.assertIn('token_type', res)

    @patch('base.application.api.user.faccess.check_facepy_library_installed', _module_installed)
    @patch('base.application.api.user.faccess.FAccess.get_user_info', _user_info)
    @patch('base.application.api.user.faccess.FAccess.social_user', FACEBOOK_USER)
    def test_f_login_after_register(self):

        _b = {
            'user': json.dumps(_FUSER, ensure_ascii=False)
        }

        body = json.dumps(_b)
        res = self.fetch('/user/f-access', method='POST', body=body)

        self.assertEqual(res.code, 200)
        res = res.body.decode('utf-8')
        res = json.loads(res)
        self.assertIn('token', res)
        self.assertIn('token_type', res)

        res2 = self.fetch('/user/f-access', method='POST', body=body)

        self.assertEqual(res2.code, 200)
        res2 = res2.body.decode('utf-8')
        res2 = json.loads(res2)
        self.assertIn('token', res2)
        self.assertIn('token_type', res2)

