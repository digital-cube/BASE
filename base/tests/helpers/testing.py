# coding: utf-8

import json
from tornado.testing import AsyncHTTPTestCase
from base.application.service import Application
from base.application.components import BaseHandler
from base.application.helpers.importer import load_application
from base.application.helpers.importer import load_orm
from base.tests.helpers.tests_manager import prepare_test_database


class TestBase(AsyncHTTPTestCase):

    def get_app(self):

        self.token = None

        entries = [(BaseHandler.__URI__, BaseHandler), ]
        load_application(entries, None)
        self.orm_builder = prepare_test_database()
        from base.config.application_config import port as svc_port
        load_orm(svc_port)

        self.load_test_hook()

        app = Application(entries, test=True)
        setattr(app, 'svc_port', svc_port)

        import os
        os.environ['ASYNC_TEST_TIMEOUT'] = '300'      # seconds for timeout

        return app

    def load_test_hook(self):
        try:
            import tests_hooks.hook
            if hasattr(tests_hooks.hook, 'register'):
                from tests_hooks.hook import register
                from types import MethodType
                setattr(self, '_register', MethodType(register, self))
        except ImportError as e:
            pass
            # print('There is no tests hook')

    def tearDown(self):
        self.stop()

    def _register(self, username, password, data=None):

        _b = {
            'username': username,
            'password': password,
            'data': data if data else {}
        }

        body = json.dumps(_b)
        res = self.fetch('/user/register', method='POST', body=body)

        self.assertEqual(res.code, 200)
        res = res.body.decode('utf-8')
        res = json.loads(res)

        self.assertIn('token', res)
        self.assertIn('token_type', res)

        self.token = res['token']

    def _check_user(self):

        self.assertIsNot(self.token, None)

        _headers = {'Authorization': self.token}

        res = self.fetch('/user/login', method='GET', body=None, headers=_headers)

        self.assertEqual(res.code, 200)
        res = res.body.decode('utf-8')
        res = json.loads(res)

        self.assertIn('id', res)

        class User:
            pass

        for _k in res:
            setattr(User, _k, res[_k])

        self._user = User()

    def get_user(self, username, password, data=None):

        self._register(username, password, data)
        self._check_user()
        return self._user

