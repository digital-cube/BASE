# coding= utf-8

import inspect
import importlib
from inspect import getmembers, isclass
from sqlalchemy.ext.declarative.api import DeclarativeMeta

from base.common.utils import log
import base.config.application_config
from base.application.components import SpecificationHandler
from base.application.components import BaseHandler
from base.application.components import PathsWriter
from base.application.helpers.exceptions import MissingApplicationConfiguration


def _load_app_configuration():
    svc_port = None
    try:
        from src.config.app_config import port
        svc_port = port
    except ImportError as e:
        log.warning('Service port not found in application configuration')

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


def load_application(entries):

    _load_app_configuration()

    from src.config.app_config import imports as app_imports

    _entries = [
        (SpecificationHandler.__URI__, SpecificationHandler),
    ]

    _has_root = False
    for _m in app_imports:

        log.info('Loading {} module'.format(_m))

        app_module = importlib.import_module(_m)

        for _name, _handler in inspect.getmembers(app_module):

            if inspect.isclass(_handler) and hasattr(_handler, '__URI__'):

                _uri = r'{}{}'.format(
                    '/{}'.format(base.config.application_config.app_prefix) if
                    getattr(_handler, '__SET_API_PREFIX__') else '',
                    getattr(_handler, '__URI__'))

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


def load_orm():

    import src.config.app_config
    import common.orm

    if not hasattr(src.config.app_config, 'db_config') or not hasattr(src.config.app_config, 'db_type'):
        raise MissingApplicationConfiguration('Missing database configuration or type')

    __db_config = src.config.app_config.db_config
    __db_type = src.config.app_config.db_type

    __db_url = common.orm.make_database_url(__db_type, __db_config['db_name'], __db_config['db_host'],
                                            __db_config['db_port'], __db_config['db_user'], __db_config['db_password'])

    common.orm.activate_orm(__db_url)

    # REMEMBER DATABASE MODELS
    for m in src.config.app_config.models:
        try:
            _m = importlib.import_module(m)
        except ImportError:
            print('Error loading model {}'.format(m))
            continue

        import config.application_config
        for _member in getmembers(_m, isclass):
            if type(_member[1]) == DeclarativeMeta and hasattr(_member[1], '__table__'):
                config.application_config.orm_models[_member[1].__table__.name] = _member[1]

