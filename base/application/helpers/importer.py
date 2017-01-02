# coding= utf-8

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
from base.application.helpers.exceptions import MissingApplicationConfiguration
from base.application.helpers.exceptions import InvalidAPIHooksModule
from base.application.helpers.exceptions import MissingRolesLookup


def _load_app_configuration(svc_port):

    try:
        from src.config.app_config import port
        svc_port = svc_port if svc_port else port
    except ImportError as e:
        # LOG FILE IS NOT CONFIGURED AND ACTIVE YET
        print('Service port not found in application configuration')

    if svc_port:
        setattr(base.config.application_config, 'port', svc_port)

    try:
        import src.config.app_config
    except ImportError:
        raise MissingApplicationConfiguration('Missing application configuration file "src.config.app_config.py"')

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
    if hasattr(src.config.app_config, 'debug'):
        setattr(base.config.application_config, 'debug', src.config.app_config.debug)
    if hasattr(src.config.app_config, 'api_hooks'):
        setattr(base.config.application_config, 'api_hooks', src.config.app_config.api_hooks)
    if hasattr(src.config.app_config, 'session_storage'):
        setattr(base.config.application_config, 'session_storage', src.config.app_config.session_storage)
    if hasattr(src.config.app_config, 'imports'):
        base.config.application_config.imports.extend(src.config.app_config.imports)
    if hasattr(src.config.app_config, 'models'):
        setattr(base.config.application_config, 'models', src.config.app_config.models)
    if hasattr(src.config.app_config, 'db_config'):
        setattr(base.config.application_config, 'db_config', src.config.app_config.db_config)
    if hasattr(src.config.app_config, 'db_type'):
        setattr(base.config.application_config, 'db_type', src.config.app_config.db_type)
    if hasattr(src.config.app_config, 'response_messages_module'):
        setattr(base.config.application_config, 'response_messages_module',
                src.config.app_config.response_messages_module)
    if hasattr(src.config.app_config, 'user_roles_module'):
        setattr(base.config.application_config, 'user_roles_module', src.config.app_config.user_roles_module)
    if hasattr(src.config.app_config, 'strong_password'):
        setattr(base.config.application_config, 'strong_password', src.config.app_config.strong_password)
    if hasattr(src.config.app_config, 'support_mail_address'):
        setattr(base.config.application_config, 'support_mail_address', src.config.app_config.support_mail_address)
    if hasattr(src.config.app_config, 'support_name'):
        setattr(base.config.application_config, 'support_name', src.config.app_config.support_name)
    if hasattr(src.config.app_config, 'forgot_password_message_subject'):
        setattr(base.config.application_config, 'forgot_password_message_subject',
                src.config.app_config.forgot_password_message_subject)
    if hasattr(src.config.app_config, 'forgot_password_message'):
        setattr(base.config.application_config, 'forgot_password_message',
                src.config.app_config.forgot_password_message)
    if hasattr(src.config.app_config, 'forgot_password_lending_address'):
        setattr(base.config.application_config, 'forgot_password_lending_address', src.config.app_config.forgot_password_lending_address)


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

    _dir = base.config.settings.log_directory
    _app = base.config.application_config.app_name
    _port = base.config.application_config.port
    _log_filename = '{}/{}_{}.log'.format(_dir, _app, _port)

    _log = base.common.utils.retrieve_log(_log_filename, base.config.settings.log_logger)
    setattr(base.common.utils, 'log', _log)

    global log
    log = _log


def load_application(entries, svc_port):

    _load_app_configuration(svc_port)
    _set_log_file()
    load_lookups()

    # LOAD APPLICATION ROUTES
    import base.config.application_config
    from base.config.application_config import imports as app_imports

    _entries = [
        (SpecificationHandler.__URI__, SpecificationHandler),
    ]

    _has_root = False
    for _m in app_imports:

        if base.config.application_config.debug:
            log.info('Loading {} module'.format(_m))

        app_module = importlib.import_module(_m)

        for _name, _handler in inspect.getmembers(app_module):

            if inspect.isclass(_handler) and hasattr(_handler, '__URI__'):

                _uri = r'{}{}'.format(
                    '/{}'.format(base.config.application_config.app_prefix) if
                    getattr(_handler, '__SET_API_PREFIX__') else '',
                    getattr(_handler, '__URI__'))

                if base.config.application_config.debug:
                    log.info('Exposing {} on {}'.format(_name, _uri))

                _entries.append((_uri, _handler))

                if _uri == '/':
                    _has_root = True

    if not _has_root:
        _entries.append((BaseHandler.__URI__, BaseHandler))

    if base.config.application_config.debug:
        _entries.append((PathsWriter.__URI__, PathsWriter))

    if len(_entries) > 1:
        del entries[:]
    entries += _entries
    # FINISH LOADING APPLICATION ROUTES

    # LOAD APPLICATION HOOKS
    try:
        _hooks_module = importlib.import_module(base.config.application_config.api_hooks)
    except ImportError:
        log.critical('Can not load api hooks file {}, missing or invalid'.format(
            base.config.application_config.api_hooks))
        raise InvalidAPIHooksModule('Missing or wrong {} API hooks module'.format(
            base.config.application_config.api_hooks))

    import base.application.api.api_hooks
    if hasattr(_hooks_module, 'hooks'):
        for _hook in _hooks_module.hooks:

            if not hasattr(_hooks_module, _hook):
                log.warning('API hook {} missing in module {}'.format(_hook, base.application.api.api_hooks))
                continue

            _real_hook = getattr(_hooks_module, _hook)
            setattr(base.application.api.api_hooks, _hook, _real_hook)
    # FINISH LOADING APPLICATION HOOKS


def load_orm():

    import base.config.application_config
    import base.common.orm

    if not hasattr(base.config.application_config, 'db_config') \
            or not hasattr(base.config.application_config, 'db_type'):
        raise MissingApplicationConfiguration('Missing database configuration or type')

    __db_config = base.config.application_config.db_config
    __db_type = base.config.application_config.db_type

    __db_url = base.common.orm.make_database_url(__db_type, __db_config['db_name'], __db_config['db_host'],
                                            __db_config['db_port'], __db_config['db_user'], __db_config['db_password'])

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

