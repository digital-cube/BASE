from base import test
import http
import base.Base
import base.orm
import base.registry


class UnitTestUsersBase(test.BaseTest):

    def setUp(self):
        base.registry.register("users", {'prefix': '/api/users', 'port': None, "db":
            {
                "type": "postgresql",
                "port": "5432",
                "host": "localhost",
                "username": "telmekom",
                "password": "123",
                "database": "telmekom_web_users"
            }})
        import api.users

        self.my_app = base.Base.make_app()

        base.registry.test = True

        db_config = base.registry.db('users')
        orm = base.orm.init_orm(db_config)
        orm.clear_database()
        orm.create_db_schema()

        super(UnitTestUsersBase, self).setUp()
        base.registry.test_port = self.get_http_port()


class TestUsersRegistration(UnitTestUsersBase):

    def test_about(self):
        self.api(None, 'GET', '/api/users/about', expected_code=http.HTTPStatus.OK)

    def test_register_user_using_users_register(self):
        r = self.api(None, 'GET', '/api/users', expected_code=http.HTTPStatus.OK)
        self.assertTrue('count' in r and r['count'] == 0)
        r = self.api(None, 'POST', '/api/users/register', body={'username': 'igor', 'password': '123'},
                     expected_code=http.HTTPStatus.CREATED)
        self.assertTrue('id' in r)
        r = self.api(None, 'GET', '/api/users', expected_code=http.HTTPStatus.OK)
        self.assertTrue('count' in r and r['count'] == 1)

    def test_register_user_using_users_crud_C(self):
        r = self.api(None, 'GET', '/api/users', expected_code=http.HTTPStatus.OK)
        self.assertTrue('count' in r and r['count'] == 0)
        r = self.api(None, 'PUT', '/api/users', body={"user": {'username': 'igor', 'password': '123'}},
                     expected_code=http.HTTPStatus.CREATED)
        self.assertTrue('id' in r)
        r = self.api(None, 'GET', '/api/users', expected_code=http.HTTPStatus.OK)
        self.assertTrue('count' in r and r['count'] == 1)


class TestUsersLogin(UnitTestUsersBase):

    def setUp(self):
        super(TestUsersLogin, self).setUp()
        r = self.api(None, 'GET', '/api/users', expected_code=http.HTTPStatus.OK)
        self.assertTrue('count' in r and r['count'] == 0)
        r = self.api(None, 'PUT', '/api/users', body={"user": {'username': 'igor', 'password': '123'}},
                     expected_code=http.HTTPStatus.CREATED)
        self.assertTrue('id' in r)
        r = self.api(None, 'GET', '/api/users', expected_code=http.HTTPStatus.OK)
        self.assertTrue('count' in r and r['count'] == 1)

    def test_login(self):
        self.api(None, 'GET', '/api/users/sessions',
                 expected_code=http.HTTPStatus.UNAUTHORIZED)

        r = self.api(None, 'PUT', '/api/users/sessions', body={'username': 'igor', 'password': '123'},
                     expected_code=http.HTTPStatus.CREATED)
        self.assertTrue('token' in r)
        token = r['token']
        r = self.api(token, 'GET', '/api/users/sessions', expected_code=http.HTTPStatus.OK)
        self.assertTrue('id_user' in r)

    def test_logout(self):
        r = self.api(None, 'PUT', '/api/users/sessions', body={'username': 'igor', 'password': '123'},
                     expected_code=http.HTTPStatus.CREATED)
        token = r['token']
        r = self.api(token, 'GET', '/api/users/sessions', expected_code=http.HTTPStatus.OK)
        self.assertTrue('id_user' in r)
        self.api(token, 'DELETE', '/api/users/sessions', expected_code=http.HTTPStatus.NO_CONTENT)
        self.api(token, 'GET', '/api/users/sessions',
                 expected_code=http.HTTPStatus.UNAUTHORIZED)
