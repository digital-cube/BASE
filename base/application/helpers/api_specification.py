# coding: utf-8
import inspect
import importlib
from base.config.application_config import imports as app_imports
from types import ModuleType


def get_api_specification(request_handler):

    import base.config.application_config

    _specification = {}

    _specification['base_version'] = base.__VERSION__
    _specification['application'] = base.config.application_config.app_name
    _specification['version'] = base.config.application_config.app_version
    _specification['prefix'] = base.config.application_config.app_prefix
    _specification['port'] = base.config.application_config.port
    _specification['application_description'] = base.config.application_config.app_description
    _specification['debug'] = base.config.application_config.debug
    _specification['api'] = {}

    from base.config.application_config import entry_points_extended
    from base.config.application_config import master

    for _m in app_imports:

        app_module = importlib.import_module(_m)
        # GET IMPORTED HANDLERS
        for _name, _handler in inspect.getmembers(app_module, inspect.isclass):

            class_name = str(_handler).split("'")[1]

            if not master and class_name in entry_points_extended and 'readonly' in entry_points_extended[class_name] and entry_points_extended[class_name]['readonly'] == False:
                continue

            # IF HANDLERS ARE FOR API
            if hasattr(_handler, '__URI__'):

                _paths = _handler.__PATH__
                for _path in _paths:

                    _specification_path = _handler.__SPECIFICATION_PATH__ if hasattr(_handler, '__SPECIFICATION_PATH__') \
                        else 'UNKNOWN_SPECIFICATION_PATH'
                    if _specification_path not in _specification['api']:
                        _specification['api'][_specification_path] = []

                    _api_prefix = _handler.__SET_API_PREFIX__

                    _api_uri = '/'.join(
                        [_u.replace(':', '{') + '}' if _u.startswith(':') else _u for _u in _path.split('/')])
                    if _api_prefix:
                        _api_uri = '/{}{}'.format(base.config.application_config.app_prefix, _api_uri)

                    methods_to_process = ('get', 'post', 'put', 'patch', 'delete')
                    if not master:
                        methods_to_process = ('get',)

                    for _f_name, _func in inspect.getmembers(_handler, inspect.isfunction):
                        if _f_name in methods_to_process:

                            from base.application.components import Base
                            _base_function = getattr(Base, _f_name)
                            if _func.__code__ != _base_function.__code__:
                                _function_specification = {}
                                _function_specification[_f_name] = {}
                                _function_specification[_f_name]['params'] = {}
                                _function_specification[_f_name]['uri'] = _api_uri
                                _function_specification[_f_name]['authenticated'] = \
                                    hasattr(_func, '__AUTHENTICATED__') and _func.__AUTHENTICATED__
                                _function_specification[_f_name]['description'] = \
                                    _func.__doc__ if _func.__doc__ else 'Missing description'

                                if hasattr(_func, '__API_DOCUMENTATION__'):

                                    for _param in _func.__API_DOCUMENTATION__:
                                        #GET PARAMETER TYPE FOR EXPORT
                                        if type(_param['type']) == str and 'sequencer:' in _param['type']:
                                            _type_name = '{} sequencer id'.format(_param['type'].split(':')[1])
                                        elif type(_param['type']) == str and _param['type'] in ['e-mail', 'json']:
                                            _type_name = _param['type']
                                        elif isinstance(_param['type'], ModuleType) and _param['type'].__name__ == 'json':
                                            _type_name = 'json'
                                        else:
                                            try:
                                                _type_name = _param['type'].__name__
                                            except AttributeError as e:
                                                print('Error get type for param "{}": {}'.format(_param, e))
                                                continue

                                        _function_specification[_f_name]['params'][_param['name']] = {}
                                        for _p in _param:
                                            _function_specification[_f_name]['params'][_param['name']][_p] = _param[_p]
                                        _function_specification[_f_name]['params'][_param['name']]['type'] = \
                                            _type_name

                                _specification['api'][_specification_path].append(_function_specification)

    return _specification
