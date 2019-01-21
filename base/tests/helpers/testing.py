# coding: utf-8

import os
import json
from functools import wraps
from tornado.testing import AsyncHTTPTestCase
from base.application.service import Application
from base.application.components import BaseHandler
from base.application.helpers.importer import load_application
from base.application.helpers.importer import load_orm
from base.common.orm import activate_orm
from base.tests.helpers.tests_manager import prepare_test_database


class db_state:
    """Make database dump records and restore if needed"""

    def __init__(self, load_from=None, save_to=None):
        self.load_from = load_from
        self.save_to = save_to

    def __call__(self, _target):

        @wraps(_target)
        def wrapper(_origin_self, *args, **kwargs):

            if self.save_to is not None:
                setattr(_origin_self, '__DB_SAVE_TO__', self.save_to)
            if self.load_from is not None:
                self.load_database_from_state(_origin_self)
            return _target(_origin_self, *args, **kwargs)

        return wrapper

    def load_database_from_dump(self, app_config, db_config, _origin_self):

        file_path = 'tests/{}'.format(self.load_from)
        __port = str(app_config.port)
        if __port not in db_config:
            raise Exception('Missing application port {} in database configuration'.format(__port))

        _db_config = db_config[__port]
        _db_name = 'test_{}'.format(_db_config['db_name']) if _db_config['db_name'][:5] != 'test_' else _db_config['db_name']

        if _db_config['db_type'] == 'mysql':
            os.system("mysql -u{} -p{} -e 'drop database {}'".format(
                _db_config['db_user'],
                _db_config['db_password'],
                _db_name
            ))
            os.system("mysql -u{} -p{} -e 'create database {}'".format(
                _db_config['db_user'],
                _db_config['db_password'],
                _db_name
            ))
            os.system('mysql {} -u{} -p{} < {}'.format(
                _db_name,
                _db_config['db_user'],
                _db_config['db_password'],
                file_path
            ))
        elif _db_config['db_type'] == 'postgresql':

            import base.common.orm
            base.common.orm.orm.engine().dispose()

            os.system('''
            if [ `PGPASSWORD={} psql -U{} -t -c "select count(*) from pg_stat_activity where datname = '{}'"` != 0 ]; 
            then echo 1 > /tmp/pgstat ; 
            else echo 0 > /tmp/pgstat ; fi'''.format( _db_config['db_password'], _db_config['db_user'], _db_name))
            with open('/tmp/pgstat') as f:
                _state = f.read()
                try:
                    _state = int(_state)
                    if _state == 1:
                        print('''
***** THERE IS AN ACTIVE CONNECTION ON {} DATABASE, PLEASE DISCONNECT AND TRY AGAIN
                        '''.format(_db_name))
                        import sys
                        sys.exit(1)

                except Exception as e:
                    pass

            os.system('''
            if [ `PGPASSWORD={} psql -U{} -t -c "select count(*) from pg_stat_activity where datname = 'template1'"` != 0 ]; 
            then echo 1 > /tmp/pgstat ; 
            else echo 0 > /tmp/pgstat ; fi'''.format( _db_config['db_password'], _db_config['db_user']))
            with open('/tmp/pgstat') as f:
                _state = f.read()
                try:
                    _state = int(_state)
                    if _state == 1:
                        print('''
***** THERE IS AN ACTIVE CONNECTION ON template1 DATABASE, PLEASE DISCONNECT AND TRY AGAIN
                        '''.format(_db_name))
                        import sys
                        sys.exit(1)

                except Exception as e:
                    pass

            os.system("PGPASSWORD={} psql -U {} template1 -c 'drop database {}' -q -o /tmp/pdb.log".format(
                _db_config['db_password'],
                _db_config['db_user'],
                _db_name
            ))
            os.system("PGPASSWORD={} psql -U {} template1 -c 'create database {}' -q -o /tmp/pdb.log".format(
                _db_config['db_password'],
                _db_config['db_user'],
                _db_name
            ))
            os.system('PGPASSWORD={} psql {} -U {} < {} -q -o /tmp/pdb.log'.format(
                _db_config['db_password'],
                _db_name,
                _db_config['db_user'],
                file_path
            ))
            from base.config.application_config import port as svc_port
            load_orm(svc_port)

        elif _db_config['db_type'] == 'sqlite':
            os.system('cp {}.db {}.db'.format(
                file_path,
                'test_{}'.format(_db_config['db_name']) if _db_config['db_name'][:5] != 'test_' else _db_config['db_name']
            ))
        else:
            print('Unknown database type {}'.format(_db_config['db_type']))
            raise Exception('Unknown database type')

    def load_database_from_state(self, _origin_self):

        file_path = 'tests/{}'.format(self.load_from)
        if not os.path.isfile(file_path):
            print('Can not find database dump file {} to load data from'.format(file_path))
            raise Exception('Can not find database dump file')

        try:
            import src.config.app_config
        except ImportError as e:
            print('Can not find application configuration, can not load database dump from file')
            raise Exception('Can not find application configuration')

        if not hasattr(src.config.app_config, 'db_config'):
            print('Missing Database configuration in config file')
            raise Exception('Missing Database configuration in config file')

        _db_config = {}
        from base.common.orm import load_database_configuration
        load_database_configuration(src.config.app_config, _db_config)

        self.load_database_from_dump(src.config.app_config, _db_config, _origin_self)


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

        os.environ['ASYNC_TEST_TIMEOUT'] = '300'  # seconds for timeout

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

    def dump_database_to_file(self, app_config, db_config):

        file_path = 'tests/{}'.format(self.__DB_SAVE_TO__)
        __port = str(app_config.port)

        if __port not in db_config:
            raise Exception('Missing application port {} in database configuration'.format(__port))

        _db_config = db_config[__port]

        if _db_config['db_type'] == 'mysql':
            os.system('mysqldump {} -u{} -p{} > {}'.format(
                'test_{}'.format(_db_config['db_name']) if _db_config['db_name'][:5] != 'test_' else _db_config['db_name'],
                _db_config['db_user'],
                _db_config['db_password'],
                file_path
            ))
        elif _db_config['db_type'] == 'postgresql':
            os.system('PGPASSWORD={} pg_dump {} -U {} > {}'.format(
                _db_config['db_password'],
                'test_{}'.format(_db_config['db_name']) if _db_config['db_name'][:5] != 'test_' else _db_config['db_name'],
                _db_config['db_user'],
                file_path
            ))
        elif _db_config['db_type'] == 'sqlite':
            os.system('cp {}.db {}.db'.format(
                'test_{}'.format(_db_config['db_name']) if _db_config['db_name'][:5] != 'test_' else _db_config['db_name'],
                file_path
            ))
        else:
            print('Unknown database type {}'.format(_db_config['db_type']))
            raise Exception('Unknown database type')

    def save_database_state(self):
        try:
            import src.config.app_config
        except ImportError as e:
            print('Can not find application configuration, can not save database dump in file')
            return

        if not hasattr(src.config.app_config, 'db_config'):
            print('Missing Database configuration in config file')
            return

        _db_config = {}
        from base.common.orm import load_database_configuration
        load_database_configuration(src.config.app_config, _db_config)

        try:
            self.dump_database_to_file(src.config.app_config, _db_config)
        except Exception as e:
            print('Can not create database dump in file tests/{}'.format(self.__DB_SAVE_TO__))
            print('Error: {}'.format(e))

    def tearDown(self):
        if hasattr(self, '__DB_SAVE_TO__') and self.__DB_SAVE_TO__ is not None:
            self.save_database_state()

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
