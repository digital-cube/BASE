# coding: utf-8

import json
from urllib.parse import urlencode
from base.tests.helpers.testing import TestBase
from base.application.lookup import responses as rmsgs


class TestSiteBase(TestBase):

    def reg(self, username, password, data):

        self.token = None
        self.get_user(username, password, data)
        self.assertIsNotNone(self.token)

        return self._user.id, self.token

    def api(self, token, method, address, body=None, expected_status_code=None, expected_result=None):

        bdy = json.dumps(body) if body else None

        if method in ('PUT'):
            if not bdy:
                bdy = '{}'

        res = self.fetch(address, method=method, body=bdy, headers={"Authorization": token} if token else {})
        if expected_status_code:
            self.assertEqual(res.code, expected_status_code)

        if not res.body:
            return None

        jres = json.loads(res.body.decode('utf-8'))

        if expected_result:
            self.assertEqual(jres, expected_result)

        return jres


class TestSite(TestSiteBase):

    def test_non_existing_page_data(self):
        id_user, token_user = self.reg('test@knowledge-base.com', '123', {'first_name': 'test',
                                                                          'last_name': 'user',
                                                                          'data': '{}',
                                                                          'role_flags': 1})

        _params = urlencode({
            'url': '/some/page'})
        r = self.api(token_user, 'GET', '/api/site/page?{}'.format(_params), expected_status_code=200)
        self.assertIn('page_meta', r)
        self.assertEqual(r['page_meta'], '')

    def test_save_page_data(self):
        id_user, token_user = self.reg('test@knowledge-base.com', '123', {'first_name': 'test',
                                                                          'last_name': 'user',
                                                                          'data': '{}',
                                                                          'role_flags': 1})

        _params = urlencode({
            'url': '/some/page',
            'html_meta': json.dumps('<meta name="test"/>')
            })

        r = self.api(token_user, 'PUT', '/api/site/page?{}'.format(_params), expected_status_code=200)
        self.assertIn('id', r)

        _params = urlencode({
            'url': '/some/page'})
        r = self.api(token_user, 'GET', '/api/site/page?{}'.format(_params), expected_status_code=200)
        self.assertIn('page_meta', r)
        self.assertEqual(r['page_meta'], '<meta name="test"/>')

    def test_save_invalid_page_data(self):
        id_user, token_user = self.reg('test@knowledge-base.com', '123', {'first_name': 'test',
                                                                          'last_name': 'user',
                                                                          'data': '{}',
                                                                          'role_flags': 1})

        _params = urlencode({
            'url': '/some/page',
            'html_meta': 'dummy string'
        })

        r = self.api(token_user, 'PUT', '/api/site/page?{}'.format(_params), expected_status_code=400)
        self.assertIn('message', r)
        self.assertEqual(r['message'], rmsgs.lmap[rmsgs.INVALID_REQUEST_ARGUMENT])

