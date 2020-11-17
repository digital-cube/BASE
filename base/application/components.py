# coding= utf-8

import os
import abc
import ast
import json
import inspect
import decimal
import datetime
import importlib
import tornado.web
import tornado.gen
import tornado.httputil
import tornado.httpclient
from functools import wraps

import base.application.lookup.responses as msgs
import base.application.lookup.authentication_level as auth_level
from base.application.helpers.exceptions import MissingApiRui
from base.application.helpers.exceptions import InvalidRequestParameter
from base.application.helpers.exceptions import MissingRequestArgument
from base.application.helpers.exceptions import DatabaseIsNotConfigured
from base.application.helpers.exceptions import MissingLanguagesLookup
from base.application.helpers.exceptions import ErrorLanguagesLookup
from base.application.helpers.exceptions import ReadOnlyAllowedOnlyForGET
from base.application.helpers.exceptions import ReadOnlyCanWrapOnlyFunction
from base.application.helpers.exceptions import WrongAuthenticationLevel
from base.common.utils import get_request_ip
from base.common.utils import retrieve_log
from base.common.sequencer import sequencer
from base.common.tokens_services import get_user_by_token


class CallCounter:
    """Count calls on uri and method"""

    def __init__(self):
        import base.config.application_config
        self.log = retrieve_log(base.config.application_config.count_call_log, 'CALL_LOG')
        self.log.info('Counter started')
        self.counter = {}
        self.start_count()

    def start_count(self):
        import base.config.application_config
        try:
            with open(base.config.application_config.count_call_file) as cf:
                try:
                    self.counter = json.load(cf)
                except Exception as e:
                    self.log.error('Error load counter log: {}'.format(e))
        except FileNotFoundError:
            self.log.info('Counter file not found, will be created')

    def write_logs(self):

        import base.config.application_config
        with open(base.config.application_config.count_call_file, 'w') as cf:
            json.dump(self.counter, cf, indent=4, sort_keys=True, ensure_ascii=False)

    def add_log(self, method, uri):
        uri = uri.split('?')[0]
        uri_and_method = self.create_log_key(method, uri)
        self.counter[uri_and_method] = 1 if uri_and_method not in self.counter else self.counter[uri_and_method] + 1
        return self.counter[uri_and_method]

    def create_log_key(self, method, uri):
        return '{}_{}'.format(method, uri)

    def get_logs(self, method, uri):
        uri = uri.split('?')[0]
        uri_and_method = self.create_log_key(method, uri)
        return 0 if uri_and_method not in self.counter else self.counter[uri_and_method]

    def __repr__(self):
        return '{}'.format(self.counter)


class Base(tornado.web.RequestHandler):
    """Base class for base application endpoints"""

    __metaclass__ = abc.ABCMeta

    def __init__(self, application, request, **kwargs):
        self.auth_token = None
        self.auth_user = None
        self.orm_session = None
        self.idx = kwargs['idx'] if 'idx' in kwargs else 0
        if 'idx' not in kwargs:
            kwargs['idx'] = 0       # for routes that have not idx set

        super(Base, self).__init__(application, request, **kwargs)

    def initialize(self, idx):
        self.idx = idx

    def prepare(self):
        import base.config.application_config
        if base.config.application_config.count_calls:
            _path = self.__FULL_PATH__ if hasattr(self, '__FULL_PATH__') else self.request.uri
            self.application.call_counter.add_log(self.request.method, _path)

    def data_received(self, chunk):
        pass

    def options(self, *args, **kwargs):

        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Methods', 'POST, PUT, PATCH, GET, DELETE, OPTIONS, LINK, UNLINK, LOCK')
        self.set_header('Access-Control-Max-Age', 1000)
        self.set_header('Access-Control-Allow-Headers',
                        'Origin, X-CSRFToken, Content-Type, Accept, Authorization, Cache-Control')
        self.set_status(200)
        self.finish('OK')

    def set_default_headers(self):

        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Methods', 'POST, PUT, PATCH, GET, DELETE, OPTIONS, LINK, UNLINK, LOCK')
        self.set_header('Access-Control-Max-Age', 1000)
        self.set_header('Access-Control-Allow-Headers',
                        'Origin, X-CSRFToken, Content-Type, Accept, Authorization, Cache-Control')

    def ok(self, s=None, **kwargs):

        _status = 204
        if s or kwargs:
            _status = 200
        elif 'http_status' in kwargs:
            _status = kwargs['http_status']
            del kwargs['http_status']
        self.set_status(_status)

        response = {}

        if isinstance(s, str):
            response['message'] = s

        if isinstance(s, dict):
            response.update(s)

        if isinstance(s, int):
            if s in msgs.lmap:
                response.update({'message': msgs.lmap[s], 'code': s})

        response.update(kwargs)

        if _status == 204:
            self.finish()
            return

        # retrieve counters
        import base.config.application_config
        if base.config.application_config.count_calls:
            _path = self.__FULL_PATH__ if hasattr(self, '__FULL_PATH__') else self.request.uri
            response['count_calls'] = self.application.call_counter.get_logs(self.request.method, _path)

        self.write(json.dumps(response, ensure_ascii=False))

    def error(self, s, **kwargs):

        from base.common.utils import log

        if 'reason' in kwargs:
            reason = kwargs['reason']
            del kwargs['reason']
        else:
            reason = 'bad request'

        _status = 400
        if 'http_status' in kwargs:
            _status = kwargs['http_status']
            del kwargs['http_status']
        self.set_status(_status, reason=reason)

        response = {}
        response['message'] = reason

        if isinstance(s, dict):
            response.update(s)
        if isinstance(s, str):
            response['message'] = s
        elif isinstance(s, int):
            if s in msgs.lmap:
                response['message'] = msgs.lmap[s]
                response['id_error'] = s
            else:
                import base.config.application_config
                _application_responses_module = base.config.application_config.response_messages_module
                try:
                    _application_responses = importlib.import_module(_application_responses_module)
                    if s in _application_responses.lmap:
                        response['message'] = _application_responses.lmap[s]
                        response['id_error'] = s
                except ImportError:
                    log.warning('Error importing {} application response messages module'.format(
                        _application_responses_module))

        response.update(kwargs)

        # retrieve counters
        import base.config.application_config
        if base.config.application_config.count_calls:
            _path = self.__FULL_PATH__ if hasattr(self, '__FULL_PATH__') else self.request.uri
            response['count_calls'] = self.application.call_counter.get_logs(self.request.method, _path)

        self.write(json.dumps(response, ensure_ascii=False))

    def write_error(self, status_code, **kwargs):

        from base.common.utils import log

        _message = msgs.lmap[msgs.EXCEPTION]

        if status_code == 405:
            log.critical('Trying to {} on {}'.format(self.request.method, self.request.uri))
            return self.error(msgs.HTTP_METHOD_NOT_ALLOWED, http_status=status_code)

        if status_code == 500:

            _error_info = kwargs['exc_info']
            _error_class = _error_info[0].__name__
            _error_value = _error_info[1]
            _exc_tb = _error_info[2]
            _file = os.path.split(_exc_tb.tb_frame.f_code.co_filename)[1]
            _list = '{}({})'.format(_file, _exc_tb.tb_lineno)
            _n = _exc_tb.tb_next
            _c = None
            while _n:
                _fname = os.path.split(_n.tb_frame.f_code.co_filename)[1]
                _list += ' -> {}({})'.format(_fname, _n.tb_lineno)
                _c = '{}({})'.format(_n.tb_frame.f_code.co_name, _n.tb_lineno)
                _n = _n.tb_next

            _message = '{} -> {} -> {}: {}'.format(_list, _c, _error_class, _error_value)
            log.critical(_message)

        import base.config.application_config
        if base.config.application_config.debug:
            return self.error(msgs.API_CALL_EXCEPTION, trace=_message, http_status=status_code)
        return self.error(msgs.API_CALL_EXCEPTION, http_status=status_code)

    def set_authorization_token(self, _auth_token):
        self.auth_token = _auth_token

    def set_authorized_user(self, auth_user):
        self.auth_user = auth_user

    def set_authorized_cookie(self, _token):
        import base.config.application_config
        import base.application.lookup.authentication_type as authentication_type
        if base.config.application_config.authentication_type == authentication_type.lmap[authentication_type.COOKIE]:
            self.set_secure_cookie(
                base.config.application_config.secret_cookie_name, _token['token'],
                domain=base.config.application_config.cookie_domain
            )

    def remove_authorized_cookie(self):
        import base.config.application_config
        import base.application.lookup.authentication_type as authentication_type
        if base.config.application_config.authentication_type == authentication_type.lmap[authentication_type.COOKIE]:
            self.clear_cookie(
                base.config.application_config.secret_cookie_name,
                domain=base.config.application_config.cookie_domain
            )


class api(object):
    """Expose API classes decorator. Setup URI for API class"""

    def __init__(self, *args, **kwargs):

        if 'URI' not in kwargs:
            import inspect
            caller_frame = inspect.stack()[1]
            raise MissingApiRui("Missing uri in API class from module {}".format(caller_frame[1]))

        self.uri = kwargs['URI']
        self.set_api_prefix = False if 'PREFIX' in kwargs and not kwargs['PREFIX'] else True
        self.specification_path = kwargs['SPECIFICATION_PATH'] if 'SPECIFICATION_PATH' in kwargs else None
        self.test_mode = kwargs['TEST_MODE'] if 'TEST_MODE' in kwargs else None

    def replace_uri_arguments(self):
        _self_uries = [self.uri] if type(self.uri) == str else self.uri

        _uries = []
        _args = []

        for _uri in _self_uries:

            _split_url = _uri.split('/')
            _res = []
            _kw_res = {}
            _mod = None
            for s in _split_url:
                if s.startswith(':'):
                    # url param is present

                    if s == ':__LANG__':
                        # url param is a language
                        from base.common.utils import log
                        import base.config.application_config
                        try:
                            _mod = importlib.import_module(base.config.application_config.languages_module)
                        except ImportError:
                            log.warning('Error loading languages module {}'.format(
                                base.config.application_config.languages_module))
                            raise MissingLanguagesLookup('Languages lookup file is missing or not configured, can not use __LANG__ variable')

                        try:
                            _path = '|'.join([lang for lang in _mod.languages_map])
                            _res.append('({})'.format(_path))
                        except Exception as e:
                            log.error('Languages module error: {}'.format(e))
                            raise ErrorLanguagesLookup('Languages lookup file badly configured')

                    else:
                        # all other url params
                        _res.append('([^/]+)')
                else:
                    # a regular part of the url path
                    _res.append(s)

                if s.startswith(':'):
                    # save url parameters indexes
                    if s[1:] == '__LANG__':
                        if not hasattr(_mod, 'language_url_param_name'):
                            log.error('Missing language url parameter name in {}'.format(_mod.__file__))
                            raise ErrorLanguagesLookup('Languages lookup file badly configured')
                        _key = _mod.language_url_param_name
                    else:
                        _key = s[1:]
                    _kw_res[_key] = _split_url.index(s) + 1 if self.set_api_prefix else _split_url.index(s)

            _uries.append('/'.join(_res))
            _args.append(_kw_res)
        return _uries, _args

    def __call__(self, cls):
        cls.__PATH__ = [self.uri] if type(self.uri) == str else self.uri
        cls.__URI__, cls.__PATH__PARAMS__ = self.replace_uri_arguments()
        cls.__SET_API_PREFIX__ = self.set_api_prefix
        cls.__SPECIFICATION_PATH__ = self.specification_path if self.specification_path is not None else cls.__name__
        cls.__ONLY_IN_TEST_MODE__ = self.test_mode

        return cls


class params(object):
    """Examine API call parameters"""

    def __init__(self, *args):
        self.params = args

    @staticmethod
    def get_sequencer_row(table, row_id):

        import base.common.orm
        import base.config.application_config
        from base.common.utils import log

        if table not in base.config.application_config.orm_models:
            log.critical('Missing table {}, can not retrieve row with id {}'.format(table, row_id))
            return None

        _orm_table = base.config.application_config.orm_models[table]

        _q = base.common.orm.orm.session().query(_orm_table).filter(_orm_table.id == row_id)
        _res = _q.all()

        if len(_res) != 1:
            log.warning('Row with id {} not found in {} table'.format(row_id, table))
            return None

        return _res[0].id

    @staticmethod
    def convert_arguments(argument, argument_value, argument_type, required):

        from base.common.utils import log

        if argument_type == bool:
            try:
                return argument_value.lower() == 'true'
            except AttributeError:
                if argument_value is None:
                    return None

                return isinstance(argument_value, bool) and argument_value

        if argument_type == int:
            if argument_value == '0':
                return 0
            try:
                return int(argument_value)
            except ValueError as e:
                log.critical('Invalid argument {} expected int got {} ({}): {}'.format(
                    argument, argument_value, type(argument_value), e))
                raise InvalidRequestParameter('Invalid argument for int')
            except TypeError as e:
                if argument_value is None:
                    return None
                log.critical('Invalid argument {} expected int got {} ({}): {}'.format(
                    argument, argument_value, type(argument_value), e))
                raise InvalidRequestParameter('Invalid argument for int')

        if argument_type == float:
            try:
                return float(argument_value)
            except ValueError as e:
                log.critical('Invalid argument {} expected float got {} ({}): {}'.format(
                    argument, argument_value, type(argument_value), e))
                raise InvalidRequestParameter('Invalid argument for float')
            except TypeError as e:
                if argument_value is None:
                    return None

                log.critical('Invalid argument {} expected float got {} ({}): {}'.format(
                    argument, argument_value, type(argument_value), e))
                raise InvalidRequestParameter('Invalid argument for float')

        if argument_type == list:

            if type(argument_value) == list:
                return argument_value

            try:
                el = ast.literal_eval(argument_value)
            except SyntaxError as e:
                log.critical('Invalid argument {} expected list, got {} ({}): {}'.format(
                    argument, argument_value, type(argument_value), e))
                raise InvalidRequestParameter('Invalid argument for list')
            except ValueError as e:
                if argument_value is None:
                    return None
                log.critical('Invalid argument {} expected list, got {} ({}): {}'.format(
                    argument, argument_value, type(argument_value), e))
                raise InvalidRequestParameter('Invalid argument for list')

            if type(el) != list:
                log.critical('Invalid argument {} expected list, got {} ({})'.format(
                    argument, argument_value, type(argument_value)))
                raise InvalidRequestParameter('Invalid argument for list')

            return el

        if argument_type == dict:
            if type(argument_value) == dict:
                return argument_value

            if type(argument_value) == str:
                try:
                    el = json.loads(argument_value)
                except json.JSONDecodeError as e:
                    log.critical('Invalid argument {} expected json, got {} ({}): {}'.format(
                        argument, argument_value, type(argument_value), e))
                    raise InvalidRequestParameter('Invalid argument for dict')

                return el

            try:
                el = ast.literal_eval(argument)
            except SyntaxError as e:
                log.critical('Invalid argument {} expected dict, got {} ({}): {}'.format(
                    argument, argument_value, type(argument_value), e))
                raise InvalidRequestParameter('Invalid argument for dict')
            except ValueError as e:
                if argument_value is None:
                    return None
                log.critical('Invalid argument {} expected list, got {} ({}): {}'.format(
                    argument, argument_value, type(argument_value), e))
                raise InvalidRequestParameter('Invalid argument for dict')

            if type(el) != dict:
                log.critical('Invalid argument {} expected dict, got {} ({})'.format(
                    argument, argument_value, type(argument_value)))
                raise InvalidRequestParameter('Invalid argument for dict')

            return el

        if argument_type == decimal.Decimal:
            try:
                return decimal.Decimal(argument_value)
            except decimal.InvalidOperation as e:
                log.critical('Invalid argument {} expected Decimal, got {} ({}): {}'.format(
                    argument, argument_value, type(argument_value), e))
                raise InvalidRequestParameter('Invalid argument for Decimal')
            except TypeError as e:
                if argument_value is None:
                    return None
                log.critical('Invalid argument {} expected Decimal, got {} ({}): {}'.format(
                    argument, argument_value, type(argument_value), e))
                raise InvalidRequestParameter('Invalid argument for Decimal')

        if argument_type == 'json' or argument_type == json:
            if argument_value is None:
                return None
            try:
                return json.loads(argument_value)
            except json.JSONDecodeError as e:
                log.critical('Invalid argument {} expected json, got {} ({}): {}'.format(
                    argument, argument_value, type(argument_value), e))
                raise InvalidRequestParameter('Invalid argument for json')
            except TypeError as e:
                # IF JSON IS SENT AND REQUEST BODY IS LOADED LIKE JSON THIS WILL BE A DICT
                if isinstance(argument_value, dict):
                    return argument_value
                else:
                    log.critical('Invalid argument {} expected json, got {} ({}): {}'.format(
                        argument, argument_value, type(argument_value), e))
                    raise InvalidRequestParameter('Invalid argument for json')

        if argument_type == 'e-mail':

            if argument_value is None:
                return None
            if '@' not in argument_value:
                log.critical('Invalid argument {} expected email, got {} ({}): {}'.format(
                    argument, argument_value, type(argument_value), 'not an e-mail'))
                raise InvalidRequestParameter('Invalid argument for E-mail')

        if argument_type == datetime.datetime:
            try:
                return datetime.datetime.strptime(argument_value, "%Y-%m-%d %H:%M:%S")
            except ValueError as e:
                log.critical('Invalid argument {} expected datetime, got {} ({}): {}'.format(
                    argument, argument_value, type(argument_value), e))
                raise InvalidRequestParameter('Invalid argument for Datetime')
            except TypeError as e:
                if argument_value is None:
                    return None
                log.critical('Invalid argument {} expected datetime, got {} ({}): {}'.format(
                    argument, argument_value, type(argument_value), e))
                raise InvalidRequestParameter('Invalid argument for Datetime')

        if argument_type == datetime.date:
            try:
                return datetime.datetime.strptime(argument_value, "%Y-%m-%d").date()
            except ValueError as e:
                log.critical('Invalid argument {} expected date, got {} ({}): {}'.format(
                    argument, argument_value, type(argument_value), e))
                raise InvalidRequestParameter('Invalid argument for Date')
            except TypeError as e:
                if argument_value is None:
                    return None
                log.critical('Invalid argument {} expected date, got {} ({}): {}'.format(
                    argument, argument_value, type(argument_value), e))
                raise InvalidRequestParameter('Invalid argument for Date')

        if argument_type == datetime.time:
            try:
                return datetime.datetime.strptime(argument_value, "%H:%M:%S").time()
            except ValueError as e:
                log.critical('Invalid argument {} expected time, got {} ({}): {}'.format(
                    argument, argument_value, type(argument_value), e))
                raise InvalidRequestParameter('Invalid argument for Time')
            except TypeError as e:
                if argument_value is None:
                    return None
                log.critical('Invalid argument {} expected time, got {} ({}): {}'.format(
                    argument, argument_value, type(argument_value), e))
                raise InvalidRequestParameter('Invalid argument for Time')

        if type(argument_type) == str and argument_type.startswith('sequencer'):

            import base.config.application_config
            if not base.config.application_config.db_configured:
                return None

            s = argument_type.split(':')
            if len(s) != 3:
                log.critical('Invalid sequence model {} for {} argument'.format(argument_type, argument))
                return None

            s_id = s[2]
            s_model = s[1]

            if not sequencer().get_sequence(s_id, argument_value):
                log.critical('Invalid argument {} expected sequencer {}, got {}'.format(argument, s_id, argument_value))
                return None

            from base.common.sequencer import SequencerFactory
            if s_model != SequencerFactory._reserved_table_name:
                return params.get_sequencer_row(s_model, argument_value)

        return argument_value

    @staticmethod
    def params_type_for_compare(_param_type):
        if _param_type in [int, float, decimal.Decimal, datetime.date, datetime.datetime, list, str]:
            return True
        return False

    @staticmethod
    def param_is_lower_then_min(_param_type, _param_value, _param_min_value, required):

        if _param_value is None and not required:
            return True

        if not params.params_type_for_compare(_param_type):
            return True
        if _param_type in [list, str]:
            try:
                if len(_param_value) < _param_min_value:
                    return False
            except Exception as e:
                return False
        elif _param_type == datetime.datetime:
            try:
                if _param_value < datetime.datetime.strptime(_param_min_value, '%Y-%m-%d %H:%M:%S'):
                    return False
            except Exception as e:
                return False
        elif _param_type == datetime.date:
            try:
                if _param_value < datetime.datetime.strptime(_param_min_value, '%Y-%m-%d').date():
                    return False
            except Exception as e:
                return False
        elif _param_value < _param_min_value:
            return False

        return True

    @staticmethod
    def param_is_greater_then_max(_param_type, _param_value, _param_max_value, required):

        if _param_value is None and not required:
            return True

        if not params.params_type_for_compare(_param_type):
            return True
        if _param_type in [list, str]:
            try:
                if len(_param_value) > _param_max_value:
                    return False
            except Exception as e:
                return False
        elif _param_type == datetime.datetime:
            try:
                if _param_value > datetime.datetime.strptime(_param_max_value, '%Y-%m-%d %H:%M:%S'):
                    return False
            except Exception as e:
                return False
        elif _param_type == datetime.date:
            try:
                if _param_value > datetime.datetime.strptime(_param_max_value, '%Y-%m-%d').date():
                    return False
            except Exception as e:
                return False
        elif _param_value > _param_max_value:
            return False
        return True

    def __call__(self, _f):

        _arguments_documentation = []

        # SAVE PARAMETERS DOCUMENTATION
        for _param in self.params:

            _argument = _param['name'].strip()
            _param_type = _param['type'] if 'type' in _param else str
            _default_param_value = _param['default'] if 'default' in _param else None
            _param_required = _param['required'] if 'required' in _param else True
            _param_min_value = _param['min'] if 'min' in _param else None
            _param_max_value = _param['max'] if 'max' in _param else None

            _arg_doc = {
                'name': _argument,
                'type': _param_type,
                'required': _param_required,
            }
            if _default_param_value:
                _arg_doc['default'] = _default_param_value
            if _param_min_value and params.params_type_for_compare(_param_type):
                _arg_doc['min'] = _param_min_value
            if _param_max_value and params.params_type_for_compare(_param_type):
                _arg_doc['max'] = _param_max_value

            _arguments_documentation.append(_arg_doc)

        # DECORATE HANDLER METHOD
        @wraps(_f)
        def wrapper(_origin_self, *args, **kwargs):

            from base.common.utils import log
            _arguments = []

            _origin_body = _origin_self.request.body
            # IF JSON IS SENT IN BODY
            _body = {}
            try:
                _body = json.loads(_origin_body.decode('utf-8'))
            except AttributeError as e:
                pass
                # log.warning('Error decoding body ->|{}|<- : {}'.format(_origin_body, e))
            except json.JSONDecodeError as e:
                pass
                # log.warning('Error loading body ->|{}|<- : {}'.format(_origin_body, e))

            for _param in self.params:

                _argument = _param['name'].strip()
                _param_type = _param['type'] if 'type' in _param else str
                _default_param_value = _param['default'] if 'default' in _param else None
                _param_required = _param['required'] if 'required' in _param else True
                _param_min_value = _param['min'] if 'min' in _param else None
                _param_max_value = _param['max'] if 'max' in _param else None
                _param_lowercase = _param['lowercase'] if 'lowercase' in _param else None
                _param_uppercase = _param['uppercase'] if 'uppercase' in _param else None

                # GET URL PARAMETERS
                if _argument in _origin_self.__PATH__PARAMS__[_origin_self.idx]:
                    _uri_param_offset = len(_origin_self.extra_prefix.split('/')) if hasattr(_origin_self, 'extra_prefix') else 0
                    _param_value = _origin_self.request.uri.split('?')[0].split('/')[
                        _origin_self.__PATH__PARAMS__[_origin_self.idx][_argument] + _uri_param_offset]
                    _param_required = True
                else:
                    # GET BODY ARGUMENTS
                    _param_value = _origin_self.get_argument(_argument, default=None)
                    if _param_value is None:
                        _param_value = _body[_argument] if _argument in _body else \
                            (_default_param_value if _default_param_value is not None else None)

                if _param_value is None and _param_required:
                    log.critical('Missing required parameter {}'.format(_argument))
                    return _origin_self.error(msgs.MISSING_REQUEST_ARGUMENT)

                try:
                    _param_converted = params.convert_arguments(_argument, _param_value, _param_type, _param_required)
                except InvalidRequestParameter as e:
                    log.critical('Invalid parameter {}'.format(_argument))
                    return _origin_self.error(msgs.INVALID_REQUEST_ARGUMENT)
                except MissingRequestArgument as e:
                    log.critical('Missing required parameter {}'.format(_argument))
                    return _origin_self.error(msgs.MISSING_REQUEST_ARGUMENT)

                if _param_min_value and not params.param_is_lower_then_min(_param_type, _param_converted,
                                                                           _param_min_value, _param_required):
                    log.warning('{} value {} is lower then required minimum {}'.format(
                        _argument, _param_value, _param_min_value))
                    return _origin_self.error(msgs.ARGUMENT_LOWER_THEN_MINIMUM)

                if _param_max_value and not params.param_is_greater_then_max(_param_type, _param_converted,
                                                                             _param_max_value, _param_required):
                    log.warning('{} value {} is greater then required maximum {}'.format(
                        _argument, _param_value, _param_min_value))
                    return _origin_self.error(msgs.ARGUMENT_HIGHER_THEN_MAXIMUM)

                if _param_lowercase:
                    try:
                        _param_converted = _param_converted.lower()
                    except AttributeError as e:
                        log.warning('Argument {} of type {} can not be converted to lowercase string'.format(
                            _param_converted, type(_param_converted)))
                        return _origin_self.error(msgs.INVALID_REQUEST_ARGUMENT)

                if _param_uppercase:
                    try:
                        _param_converted = _param_converted.upper()
                    except AttributeError as e:
                        log.warning('Argument {} of type {} can not be converted to uppercase string'.format(
                            _param_converted, type(_param_converted)))
                        return _origin_self.error(msgs.INVALID_REQUEST_ARGUMENT)

                _arguments.append(_param_converted)

            return _f(_origin_self, *_arguments, **kwargs)

        setattr(wrapper, '__API_DOCUMENTATION__', _arguments_documentation)

        return wrapper


class authenticated(object):
    """
    Make request handler methods available only to logged user
    """

    def __init__(self, *args, authentication_level=auth_level.lmap[auth_level.STRONG], redirect_url=None):

        import base.config.application_config
        if not base.config.application_config.db_configured:
            raise DatabaseIsNotConfigured(
                "Can not use authenticated decorator, database is not initialized or configured")
        if authentication_level not in auth_level.lrev:
            raise WrongAuthenticationLevel("Wrong authentication level {} provided".format(authentication_level))

        self.authentication_level = auth_level.lrev[authentication_level]
        self.redirect_url = redirect_url

        self.roles = None
        if len(args) == 1:
            self.roles = args[0]
        if len(args) > 1:
            _roles = args[0]
            for _arg in args[1:]:
                _roles |= _arg
            self.roles = _roles

    def __call__(self, _target):

        from base.common.utils import log

        if inspect.isclass(_target):

            from base.common.utils import is_implemented
            for _f_name, _func in inspect.getmembers(_target, inspect.isfunction):
                if is_implemented(_target, _f_name, _func):
                    setattr(_func, '__AUTHENTICATED__', True)
                    setattr(_target, _f_name, self.__call__(_func))

            return _target

        if inspect.isfunction(_target):

            def get_auth_token(_origin_self):
                import base.config.application_config
                import base.application.lookup.authentication_type as authentication_type

                if not base.config.application_config.test_mode and \
                        base.config.application_config.authentication_type == authentication_type.lmap[authentication_type.COOKIE]:
                    return _origin_self.get_secure_cookie(base.config.application_config.secret_cookie_name)

                return _origin_self.request.headers.get('Authorization')

            @wraps(_target)
            def wrapper(_origin_self, *args, **kwargs):

                _auth_token = get_auth_token(_origin_self)
                if type(_auth_token) == bytes:
                    _auth_token = _auth_token.decode('utf-8')
                if not _auth_token:
                    if self.authentication_level == auth_level.WEAK:
                        # if token not provided and authentication is week set auth user to None and go to the target
                        _origin_self.set_authorization_token(None)
                        _origin_self.set_authorized_user(None)
                        setattr(_target, '__AUTHENTICATED__', True)
                        return _target(_origin_self, *args, **kwargs)
                    else:
                        if self.redirect_url is not None:
                            _origin_self.redirect(self.redirect_url, permanent=False)
                            return
                        return _origin_self.error(msgs.UNAUTHORIZED_REQUEST, http_status=403)

                import base.common.orm
                with base.common.orm.orm_session() as _session:
                    if _origin_self.orm_session is None:
                        _origin_self.orm_session = _session

                    _user = get_user_by_token(_auth_token, pack=False, orm_session=_origin_self.orm_session, request_handler=_origin_self)
                    if not _user:
                        if self.authentication_level == auth_level.WEAK:
                            # if token not provided and authentication is week set auth user to None and go to the target
                            _origin_self.set_authorization_token(None)
                            _origin_self.set_authorized_user(None)
                            setattr(_target, '__AUTHENTICATED__', True)

                            import base.config.application_config
                            try:
                                # remove secure cookie if exists, because is not valid
                                _origin_self.clear_cookie(base.config.application_config.secret_cookie_name)
                            except:
                                pass

                            return _target(_origin_self, *args, **kwargs)
                        else:
                            log.critical('Can not get user from token {}'.format(_auth_token))
                            if self.redirect_url is not None:
                                _origin_self.redirect(self.redirect_url, permanent=False)
                                return

                            return _origin_self.error(msgs.UNAUTHORIZED_REQUEST, http_status=403)

                    if self.roles is not None:
                        if not (self.roles & _user.role_flags):
                            log.critical('User {} with role {} trying unauthorized access on {}'.format(
                                _user.username, _user.role_flags, _origin_self.request.uri))
                            if self.redirect_url is not None:
                                _origin_self.redirect(self.redirect_url, permanent=False)
                                return

                            return _origin_self.error(msgs.UNAUTHORIZED_REQUEST, http_status=403)

                    _origin_self.set_authorization_token(_auth_token)
                    _origin_self.set_authorized_user(_user)

                    setattr(_target, '__AUTHENTICATED__', True)

                    return _target(_origin_self, *args, **kwargs)

            return wrapper


class db(object):
    """
    Make database session available through a request handler
    """

    def __init__(self, new_session=True):

        import base.config.application_config
        if not base.config.application_config.db_configured:
            raise DatabaseIsNotConfigured(
                "Can not use db decorator, database is not initialized or configured")

        self.new_session = new_session

    def __call__(self, _target):

        if inspect.isclass(_target):

            from base.common.utils import is_implemented
            for _f_name, _func in inspect.getmembers(_target, inspect.isfunction):
                if is_implemented(_target, _f_name, _func):
                    setattr(_target, _f_name, self.__call__(_func))

            return _target

        if inspect.isfunction(_target):

            @wraps(_target)
            def wrapper(_origin_self, *args, **kwargs):

                import base.common.orm
                with base.common.orm.orm_session() as _session:

                    if _origin_self.orm_session is None:
                        _origin_self.orm_session = _session
                    return _target(_origin_self, *args, **kwargs)

            return wrapper


class RequestAuthenticationChecker(object):
    """
    Check if tornado handler is authenticated
    """

    def __init__(self, request_handler, allowed_roles):

        self.request_handler = request_handler
        self.allowed_roles = allowed_roles

    def is_authenticated(self):

        from base.common.utils import log

        _auth_token = self.request_handler.request.headers.get('Authorization')
        if not _auth_token:
            return False

        _user = get_user_by_token(_auth_token, pack=False)
        if not _user:
            log.critical('Can not get user from token {}'.format(_auth_token))
            return False

        if not (self.allowed_roles & _user.role_flags):
            log.critical('User {} with role {} trying unauthorized access on {}'.format(
                _user.username, _user.role_flags, self.request_handler.request.uri))
            return False

        self.request_handler.set_authorization_token(_auth_token)
        self.request_handler.set_authorized_user(_user)

        return True


class local(object):
    """
    Define access only to specified hosts. Default localhost
    """

    def __init__(self, host='localhost'):

        self.host = host

    def __call__(self, _f):

        from base.common.utils import log

        @wraps(_f)
        def wrapper(_origin_self, *args, **kwargs):

            remote_ip = get_request_ip(_origin_self)

            _allowed = True
            if self.host == 'localhost':
                if remote_ip not in ['localhost', '127.0.0.1']:
                    _allowed = False
            elif self.host != remote_ip:
                _allowed = False

            if not _allowed:
                log.critical('Not allowed access from {} to {} {}'.format(
                    remote_ip, _origin_self.__class__.__name__, _f.__name__))
                return _origin_self.error(msgs.NOT_ALLOWED_FROM_REMOTE)

            return _f(_origin_self, *args, **kwargs)
        return wrapper


class DefaultRouteHandler(Base):
    """Base default route handler"""

    def _dummy(self):
        method = self.request.method
        path = self.request.path
        from base.common.utils import log

        # Ignore request for favicon.ico
        if 'favicon.ico' in path:
            self.finish()
            return

        ip = self.request.remote_ip
        self.set_status(404)
        log.warning('trying to call not allowed {} method on {} uri from {}'.format(method, path, ip))
        if method == 'POST':
            return self.error(msgs.POST_NOT_FOUND)
        if method == 'PUT':
            return self.error(msgs.PUT_NOT_FOUND)
        if method == 'PATCH':
            return self.error(msgs.PATCH_NOT_FOUND)
        if method == 'DELETE':
            return self.error(msgs.DELETE_NOT_FOUND)
        return self.error(msgs.GET_NOT_FOUND)

    def get(self):
        return self._dummy()

    def post(self):
        return self._dummy()

    def put(self):
        return self._dummy()

    def patch(self):
        return self._dummy()

    def delete(self):
        return self._dummy()


@api(URI=r'/', PREFIX=False)
class BaseHandler(DefaultRouteHandler):
    """Base root route handler"""

    def _dummy(self):
        import base.config.application_config
        self.render(
            'templates/introduction.html',
            app_name=base.config.application_config.app_name,
            app_version=base.config.application_config.app_version,
            base_version=base.__VERSION__
        )


@api(URI=r'/all-paths', PREFIX=False)
class PathsWriter(DefaultRouteHandler):
    """List all paths in debug mode"""

    def _dummy(self):
        try:
            _paths = [(handler.regex.pattern, handler.handler_class) for handler in self.application.handlers[0][1]]
        except AttributeError:
            _paths = [handler for handler in self.application.default_router.application.entries]
        _paths.sort()
        _table_style = 'border-collapse: collapse;'
        _model = '<table style="{}"><tbody>'.format(_table_style)
        for _path in _paths:
            _tr = '<tr><td>{}</td><td>{}</td></tr>'
            _tr = _tr.format(_path[1].__name__, _path[0].strip('$'))
            _model += _tr

        _model += '</tbody></table>'
        self.write(_model)


@api(URI=r'/spec', PREFIX=False)
class SpecificationHandler(DefaultRouteHandler):
    """Retrieve application specification"""

    def _dummy(self):

        as_html = self.get_argument('html', default=False)

        from base.application.helpers.api_specification import get_api_specification
        _api_specification = get_api_specification(self)

        if as_html:
            self.render('templates/specification.html', spec=_api_specification)
        else:
            self.write(json.dumps(_api_specification))


class readonly(object):

    idx=0
    items=[]

    def __init__(self, *args, **kwargs):
        pass

    def __call__(self, _target, *args, **kwargs):

        if _target.__name__ != 'get':
            raise ReadOnlyAllowedOnlyForGET

        if not inspect.isfunction(_target):
            raise ReadOnlyCanWrapOnlyFunction

        import base.config.application_config
        base.config.application_config.balanced_readonly_get.add(_target)

        @wraps(_target)
        @tornado.gen.coroutine
        def wrapper(_origin_self, *args, **kwargs):

            import base.config.application_config
            # if there is no read replica on system, just return function
            if len(base.config.application_config.read_only_ports) == 0:
                return _target(_origin_self, *args, **kwargs)

            async def fetch_from_read_service(idx):
                http_client = tornado.httpclient.AsyncHTTPClient()

                url = 'http://localhost:{}{}'.format(
                    base.config.application_config.read_only_ports[
                        idx % base.config.application_config.ro_ports_length
                    ], _origin_self.request.uri)

                response = await http_client.fetch(
                    tornado.httpclient.HTTPRequest(url, headers=_origin_self.request.headers), raise_error=False
                )

                return response.code, response.body

            # master
            if base.config.application_config.master:

                import base.config.application_config
                if base.config.application_config.test_mode:
                    return _target(_origin_self, *args, **kwargs)

                if base.config.application_config.simulate_balancing:
                    status, body = yield fetch_from_read_service(readonly.idx)
                    readonly.idx += 1
                    _origin_self.set_status(status)
                    if body:
                        _origin_self.write(body.decode('utf-8'))
                    return
                else:
                    _origin_self.set_status(305)
                    return

            return _target(_origin_self, *args, **kwargs)

        return wrapper


