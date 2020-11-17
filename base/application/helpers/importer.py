# coding= utf-8

import os
import json
import inspect
import importlib
from inspect import getmembers, isclass

from sqlalchemy.ext.declarative.api import DeclarativeMeta

# LOG HAS TO BE SET DYNAMICALLY
log = None

import base.config.settings
import base.config.application_config
from base.application.components import SpecificationHandler
from base.application.components import BaseHandler
from base.application.components import PathsWriter
from base.application.helpers.exceptions import MissingDatabaseConfigurationForPort
from base.application.helpers.exceptions import MissingApplicationConfiguration
from base.application.helpers.exceptions import InvalidAPIHooksModule
from base.application.helpers.exceptions import MissingRolesLookup
from base.application.helpers.exceptions import InvalidApplicationConfiguration
from base.application.helpers.exceptions import MissingModelsConfig
from base.common.orm import load_database_configuration


def _load_app_configuration(svc_port):

    try:
        from src.config.app_config import port
        svc_port = svc_port if svc_port else port
    except ImportError as e:
        # LOG FILE IS NOT CONFIGURED AND ACTIVE YET
        print('Service port not found in application configuration')

    if svc_port:
        setattr(base.config.application_config, 'port', int(svc_port))

    try:
        import src.config.app_config
    except ImportError:
        raise MissingApplicationConfiguration('Missing application configuration file "src.config.app_config.py"')

    if hasattr(src.config.app_config, 'read_only_ports'):
        setattr(base.config.application_config, 'read_only_ports', src.config.app_config.read_only_ports)
    if hasattr(src.config.app_config, 'ro_ports_length'):
        setattr(base.config.application_config, 'ro_ports_length', src.config.app_config.ro_ports_length)

    setattr(base.config.application_config, 'master', int(svc_port) not in base.config.application_config.read_only_ports)

    if hasattr(src.config.app_config, 'app_name'):
        setattr(base.config.application_config, 'app_name', src.config.app_config.app_name)
    if hasattr(src.config.app_config, 'app_prefix'):
        setattr(base.config.application_config, 'app_prefix', src.config.app_config.app_prefix)
    if hasattr(src.config.app_config, 'app_description'):
        setattr(base.config.application_config, 'app_description', src.config.app_config.app_description)
    if hasattr(src.config.app_config, 'app_version'):
        setattr(base.config.application_config, 'app_version', src.config.app_config.app_version)
    if hasattr(src.config.app_config, 'secret_cookie'):
        setattr(base.config.application_config, 'secret_cookie', src.config.app_config.secret_cookie)
    if hasattr(src.config.app_config, 'secret_cookie_name'):
        setattr(base.config.application_config, 'secret_cookie_name', src.config.app_config.secret_cookie_name)
    if hasattr(src.config.app_config, 'debug'):
        setattr(base.config.application_config, 'debug', src.config.app_config.debug)
    if hasattr(src.config.app_config, 'api_hooks'): # todo: check this
        setattr(base.config.application_config, 'api_hooks', src.config.app_config.api_hooks)
    if hasattr(src.config.app_config, 'db_config'):
        setattr(base.config.application_config, 'db_config', src.config.app_config.db_config)
        setattr(base.config.application_config, 'db_configured', True)
        _db_is_configured = True
    else:
        setattr(base.config.application_config, 'db_configured', False)
        _db_is_configured = False
    if hasattr(src.config.app_config, 'response_messages_module'):
        setattr(base.config.application_config, 'response_messages_module',
                src.config.app_config.response_messages_module)
    if hasattr(src.config.app_config, 'support_mail_address'):
        setattr(base.config.application_config, 'support_mail_address', src.config.app_config.support_mail_address)
    if hasattr(src.config.app_config, 'support_name'):
        setattr(base.config.application_config, 'support_name', src.config.app_config.support_name)
    if hasattr(src.config.app_config, 'static_path'):
        setattr(base.config.application_config, 'static_path', src.config.app_config.static_path)
    if hasattr(src.config.app_config, 'static_uri'):
        setattr(base.config.application_config, 'static_uri', src.config.app_config.static_uri)
    if hasattr(src.config.app_config, 'log_directory '):
        setattr(base.config.application_config, 'log_directory', src.config.app_config.log_directory)
    if hasattr(src.config.app_config, 'pre_app_processes'):
        setattr(base.config.application_config, 'pre_app_processes', src.config.app_config.pre_app_processes)
    if hasattr(src.config.app_config, 'post_app_processes'):
        setattr(base.config.application_config, 'post_app_processes', src.config.app_config.post_app_processes)
    if hasattr(src.config.app_config, 'seconds_before_shutdown'):
        setattr(base.config.application_config, 'seconds_before_shutdown', src.config.app_config.seconds_before_shutdown)
    if hasattr(src.config.app_config, 'count_calls'):
        setattr(base.config.application_config, 'count_calls', src.config.app_config.count_calls)
    if hasattr(src.config.app_config, 'count_call_log'):
        setattr(base.config.application_config, 'count_call_log', src.config.app_config.count_call_log)
    if hasattr(src.config.app_config, 'count_call_file'):
        setattr(base.config.application_config, 'count_call_file', src.config.app_config.count_call_file)
    if hasattr(src.config.app_config, 'simulate_balancing'):
        setattr(base.config.application_config, 'simulate_balancing', src.config.app_config.simulate_balancing)
    if hasattr(src.config.app_config, 'service_initialisation_callbacks'):
        setattr(base.config.application_config, 'service_initialisation_callbacks',
                src.config.app_config.service_initialisation_callbacks)
    if hasattr(src.config.app_config, 'disable_spec'):
        setattr(base.config.application_config, 'disable_spec', src.config.app_config.disable_spec)
    if hasattr(src.config.app_config, 'disable_all_paths'):
        setattr(base.config.application_config, 'disable_all_paths', src.config.app_config.disable_all_paths)

    if _db_is_configured:
        _load_app_configuration_with_database(src.config.app_config)
    else:
        _load_app_configuration_without_database(src.config.app_config)


def _load_app_configuration_with_database(config_file):
    if hasattr(config_file, 'imports'):
        base.config.application_config.imports.extend(config_file.imports)
    if hasattr(config_file, 'session_storage'):
        setattr(base.config.application_config, 'session_storage', config_file.session_storage)
    if hasattr(config_file, 'models'):
        setattr(base.config.application_config, 'models', config_file.models)
    else:
        try:
            models_file = '{}/{}'.format(os.path.dirname(config_file.__file__), base.config.settings.models_config_file)
            with open(models_file) as mf:
                models = json.load(mf)
            setattr(base.config.application_config, 'models', models)
        except Exception as e:
            print('Can not read models config file "{}": {}'.format(base.config.settings.models_config_file, e))
            raise MissingModelsConfig('models.json is missing or corrupted')

    if hasattr(config_file, 'user_roles_module'):
        setattr(base.config.application_config, 'user_roles_module', config_file.user_roles_module)
    if hasattr(config_file, 'languages'):
        setattr(base.config.application_config, 'languages', config_file.languages)
    if hasattr(config_file, 'strong_password'):
        setattr(base.config.application_config, 'strong_password', config_file.strong_password)
    if hasattr(config_file, 'forgot_password_message_subject'):
        setattr(base.config.application_config, 'forgot_password_message_subject',
                config_file.forgot_password_message_subject)
    if hasattr(config_file, 'forgot_password_message'):
        setattr(base.config.application_config, 'forgot_password_message',
                config_file.forgot_password_message)
    if hasattr(config_file, 'forgot_password_lending_address'):
        setattr(base.config.application_config, 'forgot_password_lending_address',
                config_file.forgot_password_lending_address)
    if hasattr(config_file, 'register_allowed_roles') and \
            isinstance(config_file.register_allowed_roles, int):
        if not hasattr(config_file, 'registrators_allowed_roles') or \
                config_file.registrators_allowed_roles is None or \
                not isinstance(config_file.registrators_allowed_roles, int):
            raise InvalidApplicationConfiguration('Missing registrators allowed roles in the configuration file')
        setattr(base.config.application_config, 'register_allowed_roles', config_file.register_allowed_roles)
        setattr(base.config.application_config, 'registrators_allowed_roles',
                config_file.registrators_allowed_roles)
    if hasattr(config_file, 'google_client_ID'):
        setattr(base.config.application_config, 'google_client_ID', config_file.google_client_ID)
    if hasattr(config_file, 'google_discovery_docs_url'):
        setattr(base.config.application_config, 'google_discovery_docs_url', config_file.google_discovery_docs_url)
    if hasattr(config_file, 'google_check_access_token_url'):
        setattr(base.config.application_config, 'google_check_access_token_url', config_file.google_check_access_token_url)
    if hasattr(config_file, 'reload_session'):
        setattr(base.config.application_config, 'reload_session', config_file.reload_session)
    if hasattr(config_file, 'authentication_type'):
        setattr(base.config.application_config, 'authentication_type', config_file.authentication_type)
    if hasattr(config_file, 'cookie_domain'):
        setattr(base.config.application_config, 'cookie_domain', config_file.cookie_domain)
    if hasattr(config_file, 'session_expiration_timeout'):
        setattr(base.config.application_config, 'session_expiration_timeout', config_file.session_expiration_timeout)
    if hasattr(config_file, 'cached_session'):
        setattr(base.config.application_config, 'cached_session', config_file.cached_session)


def _load_app_configuration_without_database(config_file):
    if hasattr(config_file, 'imports'):
        del base.config.application_config.imports[:]
        base.config.application_config.imports.extend(config_file.imports)


def load_lookups():

    import base.config.application_config
    try:
        import base.application.lookup.user_roles
        _mod = importlib.import_module(base.config.application_config.user_roles_module)
        base.application.lookup.user_roles = _mod
    except ImportError:
        log.warning('Error loading user_roles module {}'.format(base.config.application_config.user_roles_module))
        raise MissingRolesLookup('User roles file is missing or not configured')


def _set_log_file():

    import base.common.utils
    import base.config.application_config

    _dir = base.config.application_config.log_directory
    _app = base.config.application_config.app_name
    _port = base.config.application_config.port
    _log_filename = '{}/{}_{}.log'.format(_dir, _app, _port)

    _log = base.common.utils.retrieve_log(_log_filename, base.config.settings.log_logger)
    setattr(base.common.utils, 'log', _log)

    global log
    log = _log


def load_application(entries, svc_port, test=False):

    _load_app_configuration(svc_port)
    _set_log_file()
    load_lookups()

    # LOAD APPLICATION ROUTES
    import base.config.application_config
    from base.config.application_config import imports as app_imports

    _entries = [
        (SpecificationHandler.__URI__[0], SpecificationHandler, {'idx': 0}),
    ] if not base.config.application_config.disable_spec  else []

    _has_root = False
    # exclude BASE's database dependent API
    # if base.config.application_config.db_configured:
    for _m in app_imports:

        if base.config.application_config.debug:
            log.info('Loading {} module'.format(_m))

        app_module = importlib.import_module(_m)

        for _name, _handler in inspect.getmembers(app_module):

            if inspect.isclass(_handler) and hasattr(_handler, '__URI__'):

                # ignore only test API endpoints
                if getattr(_handler, '__ONLY_IN_TEST_MODE__') and not test and not base.config.application_config.test_mode:
                    continue

                _uries = getattr(_handler, '__URI__')
                _paths = getattr(_handler, '__PATH__')
                _api_prefix = getattr(_handler, '__SET_API_PREFIX__')
                _idx = 0

                for _URI in _uries:

                    _uri = r'{}{}'.format(
                        '/{}'.format(base.config.application_config.app_prefix) if
                        _api_prefix else '',
                        _URI)

                    # for counter to work properly
                    _full_path = r'{}{}'.format(
                        '/{}'.format(base.config.application_config.app_prefix) if
                        _api_prefix else '',
                        _paths[_idx])
                    setattr(_handler, '__FULL_PATH__', _full_path)

                    if base.config.application_config.debug:
                        log.info('Exposing {} on {}'.format(_name, _uri))

                    _entries.append((_uri, _handler, {'idx': _idx}))

                    if _uri == '/':
                        _has_root = True

                    _idx += 1

    if not _has_root:
        _entries.append((BaseHandler.__URI__[0], BaseHandler, {'idx': 0}))

    if base.config.application_config.debug:
        if not base.config.application_config.disable_all_paths:
            _entries.append((PathsWriter.__URI__[0], PathsWriter, {'idx': 0}))

    if len(_entries) > 1:
        del entries[:]
    entries += _entries
    # FINISH LOADING APPLICATION ROUTES

    # LOAD APPLICATION HOOKS
    if base.config.application_config.api_hooks is None:
        return

    try:
        _hooks_module = importlib.import_module(base.config.application_config.api_hooks)
    except ImportError:
        log.critical('Can not load api hooks file {}, missing or invalid'.format(
            base.config.application_config.api_hooks))
        raise InvalidAPIHooksModule('Missing or wrong {} API hooks module'.format(
            base.config.application_config.api_hooks))

    import base.application.api_hooks.api_hooks
    if hasattr(_hooks_module, 'hooks'):
        for _hook in _hooks_module.hooks:

            if not hasattr(_hooks_module, _hook):
                log.warning('API hook {} missing in module {}'.format(_hook, base.application.api_hooks.api_hooks))
                continue

            _real_hook = getattr(_hooks_module, _hook)
            setattr(base.application.api_hooks.api_hooks, _hook, _real_hook)
    # FINISH LOADING APPLICATION HOOKS


def load_orm(svc_port, test=False, createdb=False):

    try:
        import src.config.app_config
    except ImportError:
        raise MissingApplicationConfiguration('Missing application configuration file "src.config.app_config.py"')

    import base.config.application_config
    import base.common.orm

    if not hasattr(base.config.application_config, 'db_config'):
        raise MissingDatabaseConfigurationForPort('Missing database configuration or type')

    if not hasattr(src.config.app_config, 'db_config'):
        return

    __db_config = {}
    if not load_database_configuration(src.config.app_config, __db_config):
        raise MissingDatabaseConfigurationForPort(
            '''
            Error loading database configuration from json file, 
            please initiate database or comment db_config option in the app_config''')

    svc_port = str(svc_port)
    if svc_port not in __db_config:
        raise MissingDatabaseConfigurationForPort('Missing database configuration for port {}'.format(svc_port))
    __db_config = __db_config[svc_port]
    __db_type = __db_config['db_type']

    _database_name = 'test_{}'.format(__db_config['db_name']) if test else __db_config['db_name']
    __db_url = base.common.orm.make_database_url(
        __db_type, _database_name, __db_config['db_host'], __db_config['db_port'], __db_config['db_user'],
        __db_config['db_password'], __db_config['charset'] if 'charset' in __db_config else 'utf8')

    from base.builder.maker.database_builder import _create_database
    if createdb and not _create_database(_database_name, __db_type, __db_config, test):
        print('Database has not created')

    base.common.orm.activate_orm(__db_url)

    # REMEMBER DATABASE MODELS
    for m in base.config.application_config.models:
        try:
            _m = importlib.import_module(m)
        except ImportError:
            print('Error loading model {}'.format(m))
            continue

        for _name, _model in getmembers(_m, isclass):
            if type(_model) == DeclarativeMeta and hasattr(_model, '__table__'):
                base.config.application_config.orm_models[_model.__table__.name] = _model

