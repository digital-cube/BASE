# coding: utf-8

import json
import urllib
from base.tests.helpers.testing import TestBase
import base.application.lookup.responses as msgs


class TestUserLogout(TestBase):

    def test_logout_unauthorized(self):

        self._register('user@test.loc', '123')

        body = json.dumps({})
        res = self.fetch('/user/logout', method='POST', body=body)

        self.assertEqual(res.code, 403)
        res = res.body.decode('utf-8')
        res = json.loads(res)
        self.assertIn('message', res)
        self.assertEqual(res['message'], msgs.lmap[msgs.UNAUTHORIZED_REQUEST])

    def test_logout(self):

        self._register('user@test.loc', '123')

        body = json.dumps({})
        headers = {'Authorization': self.token}
        res = self.fetch('/user/logout', method='POST', body=body, headers=headers)

        self.assertEqual(res.code, 204)
        self.assertEqual(res.body, b'')

    def test_logout_twice(self):

        self._register('user@test.loc', '123')

        body = json.dumps({})
        headers = {'Authorization': self.token}
        res = self.fetch('/user/logout', method='POST', body=body, headers=headers)

        self.assertEqual(res.code, 204)
        self.assertEqual(res.body, b'')

        res2 = self.fetch('/user/logout', method='POST', body=body, headers=headers)
        self.assertEqual(res2.code, 403)
        res2 = res2.body.decode('utf-8')
        res2 = json.loads(res2)
        self.assertIn('message', res2)
        self.assertEqual(res2['message'], msgs.lmap[msgs.UNAUTHORIZED_REQUEST])
