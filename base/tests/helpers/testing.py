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

        entries = [(BaseHandler.__URI__, BaseHandler), ]
        load_application(entries, None)
        self.orm_builder = prepare_test_database()
        from base.config.application_config import port as svc_port
        load_orm(svc_port)

        self.load_test_hook()

        return Application(entries)

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
        self.orm_builder.orm().session().close()
        self.orm_builder.clear_database()

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

