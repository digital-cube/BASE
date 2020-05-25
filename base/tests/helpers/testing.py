# coding: utf-8

import os
import json
import time
import subprocess
from functools import wraps
from tornado.testing import AsyncHTTPTestCase
from base.application.service import Application
from base.application.components import BaseHandler
from base.application.helpers.importer import load_application
from base.application.helpers.importer import load_orm
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

        file_path = '/tmp/{}'.format(self.load_from)
        __port = str(app_config.port)
        if __port not in db_config:
            raise Exception('Missing application port {} in database configuration'.format(__port))

        _db_config = db_config[__port]
        _db_name = 'test_{}'.format(_db_config['db_name']) if _db_config['db_name'][:5] != 'test_' else _db_config['db_name']

        if _db_config['db_type'] == 'mysql':
            subprocess.call(['mysql', '-u{}'.format(_db_config['db_user']), '-p{}'.format(_db_config['db_password']), '-e', "drop database {}".format(_db_name)])
            subprocess.call(['mysql', '-u{}'.format(_db_config['db_user']), '-p{}'.format(_db_config['db_password']), '-e', "create database {}".format(_db_name)])
            with open(file_path) as _in:
                subprocess.call(['mysql', _db_name, '-u{}'.format(_db_config['db_user']), '-p{}'.format(_db_config['db_password'])], stdin=_in)

        elif _db_config['db_type'] == 'postgresql':

            import base.common.orm
            base.common.orm.orm.engine().dispose()

            _pg_check = os.path.join(os.path.dirname(__file__), 'pg_check.sh')

            while True:
                subprocess.call([_pg_check, _db_config['db_password'], _db_config['db_user'], _db_name])
                with open('/tmp/pgstat') as f:
                    _state = f.read()
                    try:
                        _state = int(_state)
                        if _state == 1:
                            print('''
    ***** THERE IS AN ACTIVE CONNECTION ON {} DATABASE, PLEASE DISCONNECT AND TRY AGAIN
                            '''.format(_db_name))
                            time.sleep(1)
                            continue

                    except Exception as e:
                        time.sleep(1)
                        continue

                break

            while True:
                subprocess.call([_pg_check, _db_config['db_password'], _db_config['db_user'], 'template1'])
                with open('/tmp/pgstat') as f:
                    _state = f.read()
                    try:
                        _state = int(_state)
                        if _state == 1:
                            print('''
    ***** THERE IS AN ACTIVE CONNECTION ON template1 DATABASE, PLEASE DISCONNECT AND TRY AGAIN
                            ''')
                            time.sleep(1)
                            continue

                    except Exception as e:
                        time.sleep(1)
                        continue

                break

            _env = os.environ.copy()
            _env['PGPASSWORD'] = _db_config['db_password']

            subprocess.call(['psql', '-U', _db_config['db_user'], 'template1', '-c', 'drop database {}'.format(_db_name), '-q', '-o', '/tmp/pdb.log'], env=_env)
            subprocess.call(['psql', '-U', _db_config['db_user'], 'template1', '-c', 'create database {}'.format(_db_name), '-q', '-o', '/tmp/pdb.log'], env=_env)
            subprocess.call(['psql', '-U', _db_config['db_user'], _db_name, '-q', '-o', '/tmp/pdb.log', '-f', file_path], env=_env)
            from base.config.application_config import port as svc_port
            load_orm(svc_port)

        elif _db_config['db_type'] == 'sqlite':
            _db_name = 'test_{}'.format(_db_config['db_name']) if _db_config['db_name'][:5] != 'test_' else _db_config['db_name']
            subprocess.call(['cp', '{}.db'.format(file_path), '{}.db'.format(_db_name)])
        else:
            print('Unknown database type {}'.format(_db_config['db_type']))
            raise Exception('Unknown database type')

    def load_database_from_state(self, _origin_self):

        file_path = '/tmp/{}'.format(self.load_from)
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

    __DB_SAVE_TO__ = None

    def get_app(self):

        self.token = None

        entries = [(BaseHandler.__URI__, BaseHandler, {'idx': 0}), ]
        load_application(entries, None, test=True)
        from base.config.application_config import port as svc_port

        import base.common.orm
        if base.common.orm.orm is None:
            load_orm(svc_port, test=True, createdb=True)

        base.common.orm.orm.clear_database()
        base.common.orm.orm.create_db_schema(test=True)

        import src.config.app_config
        from base.builder.maker.common import get_orm_models
        # PRESENT MODELS TO BASE
        _models_modules = []
        _orm_models = get_orm_models(_models_modules, src.config.app_config)

        # PREPARE SEQUENCERS FIRST
        from base.builder.maker.database_builder import _get_sequencer_model_module
        import sqlalchemy.exc
        _seq_module = _get_sequencer_model_module(_models_modules)
        if _seq_module:
            try:
                _seq_module.main()
            except sqlalchemy.exc.IntegrityError:
                print('Sequencer already contains keys, and will not be inserted again, continuing')

        # PREPARE SEQUENCERS FIRST
        for _module in _models_modules:
            if hasattr(_module, 'main'):
                _module.main()

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
        except ImportError:
            pass

    def dump_database_to_file(self, app_config, db_config):

        file_path = '/tmp/{}'.format(self.__DB_SAVE_TO__)
        __port = str(app_config.port)

        if __port not in db_config:
            raise Exception('Missing application port {} in database configuration'.format(__port))

        _db_config = db_config[__port]

        if _db_config['db_type'] == 'mysql':
            _db_name = 'test_{}'.format(_db_config['db_name']) if _db_config['db_name'][:5] != 'test_' else _db_config['db_name']
            with open(file_path, 'w+') as _out:
                subprocess.call(['mysqldump', _db_name, '-u{}'.format(_db_config['db_user']), '-p{}'.format(_db_config['db_password'])], stdout=_out)
        elif _db_config['db_type'] == 'postgresql':
            _env = os.environ.copy()
            _env['PGPASSWORD'] = _db_config['db_password']
            _db_name = 'test_{}'.format(_db_config['db_name']) if _db_config['db_name'][:5] != 'test_' else _db_config['db_name']
            with open(file_path, 'w+') as _out:
                subprocess.call(['pg_dump', _db_name, '-U', _db_config['db_user']], stdout=_out)
        elif _db_config['db_type'] == 'sqlite':
            _db_name = 'test_{}'.format(_db_config['db_name']) if _db_config['db_name'][:5] != 'test_' else _db_config['db_name']
            subprocess.call(['cp', '{}.db'.format(_db_name), '{}.db'.format(file_path)])
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
            print('Can not create database dump in file /tmp/{}'.format(self.__DB_SAVE_TO__))
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
