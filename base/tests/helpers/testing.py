# coding: utf-8

from tornado.testing import AsyncHTTPTestCase
from base.application.service import Application
from base.application.components import BaseHandler
from base.application.helpers.importer import load_application
from base.application.helpers.importer import load_orm
from base.tests.helpers.tests_manager import prepare_test_database


class TestBase(AsyncHTTPTestCase):

    def get_app(self):

        entries = [(BaseHandler.__URI__, BaseHandler), ]
        load_application(entries)
        self.orm_builder = prepare_test_database()
        load_orm()

        return Application(entries)

    def tearDown(self):
        self.stop()
        self.orm_builder.orm().session().close()
        self.orm_builder.clear_database()


