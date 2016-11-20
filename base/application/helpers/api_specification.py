import copy
import inspect
import importlib
from src.config.app_config import imports as app_imports

def get_api_specification(request_handler):

    import base.config.application_config

    _specification = {}

    _specification['application'] = base.config.application_config.app_name
    _specification['version'] = base.config.application_config.app_version
    _specification['prefix'] = base.config.application_config.app_prefix
    _specification['port'] = base.config.application_config.port
    _specification['application_description'] = base.config.application_config.app_description
    _specification['debug'] = base.config.application_config.debug
    _specification['api'] = {}

    for _m in app_imports:

        app_module = importlib.import_module(_m)
        # GET IMPORTED HANDLERS
        for _name, _handler in inspect.getmembers(app_module, inspect.isclass):

            # IF HANDLERS ARE FOR API
            if hasattr(_handler, '__URI__'):

                _specification_path = _handler.__SPECIFICATION_PATH__ if hasattr(_handler, '__SPECIFICATION_PATH__') \
                    else 'UNKONWN_SPECIFICATION_PATH'
                if _specification_path not in _specification['api']:
                    _specification['api'][_specification_path] = []

                # _api_prefix = _handler.__SET_API_PREFIX__
                # _query_params = _handler.__PATH__PARAMS__
                _api_uri = '/'.join(
                    [_u.replace(':','{') + '}' if _u.startswith(':') else _u for _u in _handler.__PATH__.split('/')])

                for _f_name, _func in inspect.getmembers(_handler, inspect.isfunction):
                    if _f_name in ('get', 'post', 'put', 'patch', 'delete'):
                        from application.components import Base
                        _base_function = getattr(Base, _f_name)
                        if _func.__code__ != _base_function.__code__:
                            _function_specification = {}
                            _function_specification[_f_name] = {}
                            _function_specification[_f_name]['params'] = {}
                            _function_specification[_f_name]['uri'] = _api_uri
                            _function_specification[_f_name]['autenticated'] = False
                            _function_specification[_f_name]['description'] = \
                                _func.__doc__ if _func.__doc__ else 'Missing description'

                            if hasattr(_func, '__API_DOCUMENTATION__'):

                                for _param in _func.__API_DOCUMENTATION__:
                                    #GET PARAMETER TYPE FOR EXPORT
                                    _type_name = '{} sequencer id'.format(_param['type'].split(':')[1]) \
                                        if type(_param['type']) == str and 'sequencer:' in _param['type'] \
                                        else _param['type'].__name__

                                    _function_specification[_f_name]['params'][_param['name']] = \
                                        copy.deepcopy(_param)
                                    _function_specification[_f_name]['params'][_param['name']]['type'] = \
                                        _type_name

                            _specification['api'][_specification_path].append(_function_specification)

    return _specification
