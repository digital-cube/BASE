# coding: utf-8

import json
from base.tests.helpers.testing import TestBase
import base.application.lookup.responses as msgs


class TestHash2Params(TestBase):

    def _set_h2p(self):

        self._h2p_data = json.dumps({'value': '123'})
        _b = {
            'data': self._h2p_data
        }
        body = json.dumps(_b)
        headers = {'Authorization': self.token}
        res = self.fetch('/tools/h2p', method='PUT', body=body, headers=headers)

        self.assertEqual(res.code, 200)
        res = res.body.decode('utf-8')
        res = json.loads(res)

        self.assertIn('h2p', res)
        self._h2p = res['h2p']

    def test_set_h2p_unauthorized(self):

        _b = {
            'value': '123'
        }

        body = json.dumps(_b)
        res = self.fetch('/tools/h2p', method='PUT', body=body)

        self.assertEqual(res.code, 403)
        res = res.body.decode('utf-8')
        res = json.loads(res)

        self.assertIn('message', res)
        self.assertEqual(res['message'], msgs.lmap[msgs.UNAUTHORIZED_REQUEST])

    def test_save_hash(self):

        self._register('user@test.loc', '123')

        _b = {
            'data': json.dumps({'test': 'data'})
        }
        _body = json.dumps(_b)
        headers = {'Authorization': self.token}
        res = self.fetch('/tools/h2p', method='PUT', body=_body, headers=headers)

        self.assertEqual(res.code, 200)
        res = res.body.decode('utf-8')
        res = json.loads(res)

        self.assertIn('h2p', res)

    def test_get_hash_data(self):

        self._register('user@test.loc', '123')
        self._set_h2p()

        headers = {'Authorization': self.token}
        res = self.fetch('/tools/h2p/{}'.format(self._h2p), method='GET', headers=headers)

        self.assertEqual(res.code, 200)
        res = res.body.decode('utf-8')
        res = json.loads(res)

        self.assertIn('value', res)
        self.assertEqual(res['value'], '123')

    def test_get_unexisting_hash(self):

        self._register('user@test.loc', '123')

        headers = {'Authorization': self.token}
        res = self.fetch('/tools/h2p/xxx', method='GET', headers=headers)

        self.assertEqual(res.code, 204)
        res = res.body.decode('utf-8')

        self.assertEqual(res, '')
        self.assertEqual(len(res), 0)
