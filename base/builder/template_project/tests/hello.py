# coding: utf-8

import json
from base.tests.helpers.testing import TestBase


class TestHello(TestBase):

    def test_get(self):

        res = self.fetch('/api/hello')

        self.assertEqual(res.code, 200)
        res = res.body.decode('utf-8')
        res = json.loads(res)

        self.assertIn('message', res)
        self.assertIn(res['message'], 'hello get')

    def test_post(self):

        res = self.fetch('/api/hello', method='POST', body='')

        self.assertEqual(res.code, 200)
        res = res.body.decode('utf-8')
        res = json.loads(res)

        self.assertIn('message', res)
        self.assertIn(res['message'], 'hello post')

    def test_put(self):

        res = self.fetch('/api/hello', method='PUT', body='')

        self.assertEqual(res.code, 200)
        res = res.body.decode('utf-8')
        res = json.loads(res)

        self.assertIn('message', res)
        self.assertIn(res['message'], 'hello put')

    def test_patch(self):

        res = self.fetch('/api/hello', method='PATCH', body='')

        self.assertEqual(res.code, 200)
        res = res.body.decode('utf-8')
        res = json.loads(res)

        self.assertIn('message', res)
        self.assertIn(res['message'], 'hello patch')

    def test_delete(self):

        res = self.fetch('/api/hello', method='DELETE')

        self.assertEqual(res.code, 200)
        res = res.body.decode('utf-8')
        res = json.loads(res)

        self.assertIn('message', res)
        self.assertIn(res['message'], 'hello delete')

