from base import test
import http
import base.Base
import base.orm
import base.registry
import unittest

from unittest.mock import patch

random_uuid = '00000000-0000-0000-0420-000000000000'

id_user = '00000000-0000-0000-0000-000000000001'
id_session = '00000000-0000-0000-0000-000000000002'


def token2user(_):
    return True, id_user, id_session


class UnitTestMailerBase(test.BaseTest):

    def setUp(self):
        import base.base_redis as redis
        r = redis.Redis()
        r.flushall()

        base.registry.register("mailer", {'prefix': '/api/mailer', 'port': None,
                                          'sendgrid_api_key': '--sendgridapikey--',
                                          "db":
                                              {
                                                  "type": "postgresql",
                                                  "port": "5432",
                                                  "host": "localhost",
                                                  "username": "sfscon",
                                                  "password": "123",
                                                  "database": "sfscon_mailer"
                                              }})
        import api.mailer

        self.my_app = base.Base.make_app()

        base.registry.test = True

        db_config = base.registry.db('mailer')
        orm = base.orm.init_orm(db_config)
        orm.clear_database()
        orm.create_db_schema()

        super().setUp()
        base.registry.test_port = self.get_http_port()


@patch('base.token.token2user', token2user)
class TestMailer(UnitTestMailerBase):

    def test_about(self):
        self.api(None, 'GET', '/api/mailer/about', expected_code=http.HTTPStatus.OK)

    def test_send(self):
        r = self.api(None, 'PUT', '/api/mailer', body={
            'mail': {'sender_email': 'digital@digitalcube.rs',
                     'receiver_email': 'igor@digitalcube.rs',
                     'subject': 'test',
                     'body': 'test test'}
        } , expected_code=http.HTTPStatus.CREATED)


if __name__ == '__main__':
    unittest.main()
