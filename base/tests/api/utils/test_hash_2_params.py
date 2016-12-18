# coding: utf-8

import json
from base.tests.helpers.testing import TestBase
import base.application.lookup.responses as msgs


class TestHash2Params(TestBase):

    def _set_h2p(self):

        _b = {
            'value': '123'
        }
        body = json.dumps(_b)
        headers = {'Authorization': self.token}
        res = self.fetch('/h2p', method='PUT', body=body, headers=headers)

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
        res = self.fetch('/h2p', method='PUT', body=body)

        self.assertEqual(res.code, 400)
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
        res = self.fetch('/h2p', method='PUT', body=_body, headers=headers)

        self.assertEqual(res.code, 200)
        res = res.body.decode('utf-8')
        res = json.loads(res)
        # print('RES', res)

        self.assertIn('h2p', res)

    # def test_get_option(self):
    #
    #     self._register()
    #     self._set_option()
    #
    #     headers = {'Authorization': self.token}
    #     res = self.fetch('/option/test_option', method='GET', headers=headers)
    #
    #     self.assertEqual(res.code, 200)
    #     res = res.body.decode('utf-8')
    #     res = json.loads(res)
    #
    #     self.assertIn('test_option', res)
    #     self.assertEqual(res['test_option'], '321')
    #
    # def test_get_unexisting_option(self):
    #
    #     self._register()
    #     self._set_option()
    #
    #     headers = {'Authorization': self.token}
    #     res = self.fetch('/option/test_option_not_exists', method='GET', headers=headers)
    #
    #     self.assertEqual(res.code, 400)
    #     res = res.body.decode('utf-8')
    #     res = json.loads(res)
    #
    #     self.assertIn('option', res)
    #     self.assertEqual(res['option'], 'test_option_not_exists')
    #     self.assertIn('message', res)
    #     self.assertEqual(res['message'], msgs.lmap[msgs.MISSING_OPTION])
