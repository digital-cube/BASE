# coding: utf-8

import json
from base.tests.helpers.testing import TestBase
import base.application.lookup.responses as msgs


class TestUserChangePassword(TestBase):

    def _forgot(self):

        _b = {
            'username': 'user@test.loc',
            'data': {'additional': 'additional_data'}
        }

        body = json.dumps(_b)
        res = self.fetch('/user/forgot', method='PUT', body=body)

        self.assertEqual(res.code, 204)
        res = res.body.decode('utf-8')
        self.assertEqual(res, '')

    def _login_success(self, password):

        _b = {
            'username': 'user@test.loc',
            'password': password
        }

        body = json.dumps(_b)
        res = self.fetch('/user/login', method='POST', body=body)

        self.assertEqual(res.code, 200)
        res = res.body.decode('utf-8')
        res = json.loads(res)

        self.assertIn('token', res)

    def _login_error(self, password):

        _b = {
            'username': 'user@test.loc',
            'password': password
        }

        body = json.dumps(_b)
        res = self.fetch('/user/login', method='POST', body=body)

        self.assertEqual(res.code, 400)
        res = res.body.decode('utf-8')
        res = json.loads(res)

        self.assertIn('message', res)
        self.assertEqual(res['message'], msgs.lmap[msgs.WRONG_USERNAME_OR_PASSWORD])

    def test_change_password_from_forgot_password_flow(self):

        self._register('user@test.loc', '123')
        self._forgot()

        import base.common.orm
        H2P = base.common.orm.get_orm_model('hash_2_params')

        with base.common.orm.orm_session() as _session:
            _q = _session.query(H2P)
            self.assertEqual(1, _q.count())
            _h2p = _q.one()

        _url ='/user/password/change/{}'.format(_h2p.hash)
        body = json.dumps({'new_password': '321'})
        res = self.fetch(_url, method='POST', body=body)

        self.assertEqual(res.code, 204)
        res = res.body.decode('utf-8')
        self.assertEqual(res, '')

        self._login_success('321')
        self._login_error('123')

    def test_change_password_with_forgot_twice(self):

        self._register('user@test.loc', '123')
        self._forgot()

        import base.common.orm
        H2P = base.common.orm.get_orm_model('hash_2_params')
        with base.common.orm.orm_session() as _session:
            _q = _session.query(H2P)
            self.assertEqual(1, _q.count())
            _h2p = _q.one()

        _url ='/user/password/change/{}'.format(_h2p.hash)
        body = json.dumps({'new_password': '321'})
        res = self.fetch(_url, method='POST', body=body)

        self.assertEqual(res.code, 204)
        res = res.body.decode('utf-8')
        self.assertEqual(res, '')

        res = self.fetch(_url, method='POST', body=body)

        self.assertEqual(res.code, 204)
        res = res.body.decode('utf-8')
        self.assertEqual(res, '')

        self._login_success('321')
        self._login_error('123')

    def test_change_password_with_wrong_hash(self):

        self._register('user@test.loc', '123')
        self._forgot()

        _url ='/user/password/change/xxxxx'
        body = json.dumps({'new_password': '321'})
        res = self.fetch(_url, method='POST', body=body)

        self.assertEqual(res.code, 400)
        res = res.body.decode('utf-8')
        res = json.loads(res)
        self.assertIn('message', res)
        self.assertEqual(res['message'], msgs.lmap[msgs.CHANGE_PASSWORD_ERROR])

        self._login_success('123')
        self._login_error('321')

    def test_user_change_password(self):

        self._register('user@test.loc', '123')

        body = json.dumps({
            'new_password': '321',
            'old_password': '123',
        })

        headers = {'Authorization': self.token}
        res = self.fetch('/user/password/change', method='POST', body=body, headers=headers)

        self.assertEqual(res.code, 204)
        res = res.body.decode('utf-8')
        self.assertEqual(res, '')

        self._login_success('321')
        self._login_error('123')

    def test_user_change_password_with_wrong_old_password(self):

        self._register('user@test.loc', '123')

        body = json.dumps({
            'new_password': '321',
            'old_password': '124',
        })

        headers = {'Authorization': self.token}
        res = self.fetch('/user/password/change', method='POST', body=body, headers=headers)

        self.assertEqual(res.code, 403)
        res = res.body.decode('utf-8')
        res = json.loads(res)
        self.assertIn('message', res)
        self.assertEqual(res['message'], msgs.lmap[msgs.UNAUTHORIZED_REQUEST])

        self._login_success('123')
        self._login_error('321')

