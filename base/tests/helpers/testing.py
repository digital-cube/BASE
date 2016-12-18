# coding: utf-8

import json
import urllib
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
        load_orm()

        return Application(entries)

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
        res = self.fetch('/register', method='POST', body=body)

        self.assertEqual(res.code, 200)
        res = res.body.decode('utf-8')
        res = json.loads(res)

        self.assertIn('token', res)
        self.assertIn('token_type', res)

        self.token = res['token']

