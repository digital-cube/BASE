# coding= utf-8

import inspect
import importlib

from base.common.utils import log
import base.config.application_config
from base.application.components import SpecificationHandler


def _load_app_configuration():
    svc_port = None
    try:
        from src.config.app_config import port
        svc_port = port
    except ImportError as e:
        log.warning('Service port not found in application configuration')

    if svc_port:
        setattr(base.config.application_config, 'port', svc_port)

    import src.config.app_config

    if hasattr(src.config.app_config, 'app_name'):
        setattr(base.config.application_config, 'app_name', src.config.app_config.app_name)
    if hasattr(src.config.app_config, 'app_prefix'):
        setattr(base.config.application_config, 'app_prefix', src.config.app_config.app_prefix)
    if hasattr(src.config.app_config, 'app_description'):
        setattr(base.config.application_config, 'app_description', src.config.app_config.app_description)
    if hasattr(src.config.app_config, 'app_version'):
        setattr(base.config.application_config, 'app_version', src.config.app_config.app_version)


def load_application(entries):

    _load_app_configuration()

    from src.config.app_config import imports as app_imports

    _entries = [
        (r'/spec', SpecificationHandler)
    ]

    for _m in app_imports:

        log.info('Loadin {} module'.format(_m))

        app_module = importlib.import_module(_m)

        for _name, _handler in inspect.getmembers(app_module):

            if inspect.isclass(_handler) and hasattr(_handler, '__URI__'):

                _uri = '{}{}'.format(
                    '/{}'.format(base.config.application_config.app_prefix) if
                    getattr(_handler, '__SET_API_PREFIX__') else '',
                    getattr(_handler, '__URI__'))

                log.info('Exposing {} on {}'.format(_name, _uri))
                _entries.append((_uri, _handler))

    if len(_entries) > 1:
        del entries[:]
    entries += _entries



