# coding: utf-8

import json
from unittest.mock import patch
from base.tests.helpers.testing import TestBase
import base.application.lookup.responses as msgs


GOOGLE_URLS = {
    'userinfo_endpoint': 'http://xxxx'
}

GOOGLE_USER = {
    'email': 'dummy@test.com',
}

FALSE_CONFIG = {
    'google_client_ID': None,
    'count_calls': False
}


def get_mock_app_config(google_client_ID):

    return {
        'google_client_ID': google_client_ID,
        'count_calls': False
    }


def _is_configured(self):
    return True


def _is_not_configured(self):
    return False


def _token_verified(self):
    return True


def _token_not_verified(self):
    return False


def _user_info(self):
    return True


def _user_info_error(self):
    return False


def _log_in_user(self):
    return {
        'token': 'xxx',
        'token_type': 'xxx'
    }


def _log_in_user_error(self):
    return False


class TestUserGAccess(TestBase):

    @patch('base.config.application_config', **get_mock_app_config(None))
    def test_with_missing_config(self, r):

        _b = {
            'token': 'xxx',
        }

        body = json.dumps(_b)
        res = self.fetch('/user/g-access', method='POST', body=body)

        self.assertEqual(res.code, 400)
        res = res.body.decode('utf-8')
        res = json.loads(res)
        self.assertIn('message', res)
        self.assertEqual(res['message'], msgs.lmap[msgs.MISSING_GACCESS_CONFIGURATION])

    @patch('base.config.application_config', **get_mock_app_config('xxx'))
    @patch('base.application.api.user.gaccess.GAccess.is_configured', _is_not_configured)
    def test_g_access_configured_but_not_getting_addresses(self, r):

        _b = {
            'token': 'xxx'
        }

        body = json.dumps(_b)
        res = self.fetch('/user/g-access', method='POST', body=body)

        # import pdb; pdb.set_trace()
        self.assertEqual(res.code, 400)
        res = res.body.decode('utf-8')
        res = json.loads(res)
        self.assertIn('message', res)
        self.assertEqual(res['message'], msgs.lmap[msgs.ERROR_READ_GACCESS_CONFIGURATION])

    @patch('base.config.application_config', **get_mock_app_config('xxx'))
    @patch('base.application.api.user.gaccess.GAccess.is_configured', _is_configured)
    @patch('base.application.api.user.gaccess.GAccess.verify_token', _token_not_verified)
    def test_g_access_token_not_verified(self, r):

        _b = {
            'token': 'xxx'
        }

        body = json.dumps(_b)
        res = self.fetch('/user/g-access', method='POST', body=body)

        # import pdb; pdb.set_trace()
        self.assertEqual(res.code, 400)
        res = res.body.decode('utf-8')
        res = json.loads(res)
        self.assertIn('message', res)
        self.assertEqual(res['message'], msgs.lmap[msgs.ERROR_VERIFY_GOOGLE_ACCESS_TOKEN])

    @patch('base.config.application_config', **get_mock_app_config('xxx'))
    @patch('base.application.api.user.gaccess.GAccess.is_configured', _is_configured)
    @patch('base.application.api.user.gaccess.GAccess.verify_token', _token_verified)
    @patch('base.application.api.user.gaccess.GAccess.get_user_info', _user_info_error)
    @patch('base.application.api.user.gaccess.GAccess.GOOGLE_URLS', GOOGLE_URLS)
    def test_g_access_can_not_fetch_user_data(self, r):

        _b = {
            'token': 'xxx'
        }

        body = json.dumps(_b)
        res = self.fetch('/user/g-access', method='POST', body=body)

        # import pdb; pdb.set_trace()
        self.assertEqual(res.code, 400)
        res = res.body.decode('utf-8')
        res = json.loads(res)
        self.assertIn('message', res)
        self.assertEqual(res['message'], msgs.lmap[msgs.ERROR_GET_GOOGLE_USER])

    @patch('base.config.application_config', **get_mock_app_config('xxx'))
    @patch('base.application.api.user.gaccess.GAccess.is_configured', _is_configured)
    @patch('base.application.api.user.gaccess.GAccess.verify_token', _token_verified)
    @patch('base.application.api.user.gaccess.GAccess.get_user_info', _user_info)
    @patch('base.application.api.user.gaccess.GAccess.GOOGLE_URLS', GOOGLE_URLS)
    @patch('base.application.api.user.gaccess.GAccess.log_user_in', _log_in_user_error)
    @patch('base.application.api.user.gaccess.GAccess.social_user', GOOGLE_USER)
    def test_g_access_can_not_register_or_login_user(self, r):

        _b = {
            'token': 'xxx'
        }

        body = json.dumps(_b)
        res = self.fetch('/user/g-access', method='POST', body=body)

        # import pdb; pdb.set_trace()
        self.assertEqual(res.code, 400)
        res = res.body.decode('utf-8')
        res = json.loads(res)
        self.assertIn('message', res)
        self.assertEqual(res['message'], msgs.lmap[msgs.ERROR_AUTHORIZE_GOOGLE_USER])

    @patch('base.config.application_config', **get_mock_app_config('xxx'))
    @patch('base.application.api.user.gaccess.GAccess.is_configured', _is_configured)
    @patch('base.application.api.user.gaccess.GAccess.verify_token', _token_verified)
    @patch('base.application.api.user.gaccess.GAccess.get_user_info', _user_info)
    @patch('base.application.api.user.gaccess.GAccess.GOOGLE_URLS', GOOGLE_URLS)
    @patch('base.application.api.user.gaccess.GAccess.log_user_in', _log_in_user)
    @patch('base.application.api.user.gaccess.GAccess.social_user', GOOGLE_USER)
    def test_g_access(self, r):

        _b = {
            'token': 'xxx'
        }

        body = json.dumps(_b)
        res = self.fetch('/user/g-access', method='POST', body=body)

        # import pdb; pdb.set_trace()
        self.assertEqual(res.code, 200)
        res = res.body.decode('utf-8')
        res = json.loads(res)
        self.assertIn('token', res)
        self.assertIn('token_type', res)

    @patch('base.config.application_config', **get_mock_app_config('xxx'))
    @patch('base.application.api.user.gaccess.GAccess.is_configured', _is_configured)
    @patch('base.application.api.user.gaccess.GAccess.verify_token', _token_verified)
    @patch('base.application.api.user.gaccess.GAccess.get_user_info', _user_info)
    @patch('base.application.api.user.gaccess.GAccess.GOOGLE_URLS', GOOGLE_URLS)
    @patch('base.application.api.user.gaccess.GAccess.log_user_in', _log_in_user)
    @patch('base.application.api.user.gaccess.GAccess.social_user', GOOGLE_USER)
    def test_g_access_after_first_register(self, r):

        _b = {
            'token': 'xxx'
        }

        body = json.dumps(_b)
        res = self.fetch('/user/g-access', method='POST', body=body)

        # import pdb; pdb.set_trace()
        self.assertEqual(res.code, 200)
        res = res.body.decode('utf-8')
        res = json.loads(res)
        self.assertIn('token', res)
        self.assertIn('token_type', res)

        res1 = self.fetch('/user/g-access', method='POST', body=body)

        # import pdb; pdb.set_trace()
        self.assertEqual(res1.code, 200)
        res1 = res1.body.decode('utf-8')
        res1 = json.loads(res1)
        self.assertIn('token', res1)
        self.assertIn('token_type', res1)


