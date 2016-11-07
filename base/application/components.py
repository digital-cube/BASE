# coding= utf-8

import os
import abc
import ast
import json
import decimal
import datetime
import tornado.web
from functools import wraps

import base.application.lookup.responses
import base.application.lookup.responses as msgs
from base.application.helpers.exceptions import MissingApiRui
from base.common.utils import log


class Base(tornado.web.RequestHandler):
    """Base class for base application endpoints"""

    __metaclass__ = abc.ABCMeta

    def data_received(self, chunk):
        pass

    # UNCOMMENT THIS METHOD IF NEEDED
    # def options(self, *args, **kwargs):
    #
    #     self.set_status(200)
    #     self.set_header('Access-Control-Allow-Origin', '*')
    #     self.set_header('Access-Control-Allow-Methods', 'POST, PUT, PATCH, GET, DELETE, OPTIONS')
    #     self.set_header('Access-Control-Max-Age', 1000)
    #     self.set_header('Access-Control-Allow-Headers', 'Origin, X-CSRFToken, Content-Type, Accept, Authorization')
    #     self.finish('OK')

    def ok(self, s=None, **kwargs):

        if 'http_status' in kwargs:
            self.set_status(kwargs['http_status'])
            del kwargs['http_status']
        elif s or kwargs:
            self.set_status(200)
        else:
            self.set_status(204)

        response = {}

        if isinstance(s, str):
            response['message'] = s

        if isinstance(s, dict):
            response.update(s)

        if isinstance(s, int):
            if s in base.application.lookup.responses.lmap:
                response.update({'message': base.application.lookup.responses.lmap[s], 'code': s})

        response.update(kwargs)

        self.write(json.dumps(response, ensure_ascii=False))

    def error(self, s, **kwargs):

        if 'reason' in kwargs:
            reason = kwargs['reason']
            del kwargs['reason']
        else:
            reason = 'bad request'

        if 'http_status' in kwargs:
            self.set_status(kwargs['http_status'], reason=reason)
            del kwargs['http_status']
        else:
            self.set_status(400, reason=reason)

        response = {}
        response['message'] = reason

        if isinstance(s, str):
            response['message'] = s
        elif isinstance(s, int):
            if s in base.application.lookup.responses.lmap:
                response['message'] = base.application.lookup.responses.lmap[s]

        response.update(kwargs)

        self.write(json.dumps(response, ensure_ascii=False))

    def write_error(self, status_code, **kwargs):

        _message = msgs.lmap[msgs.EXCEPTION]
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


class SpecificationHandler(tornado.web.RequestHandler):
    """Retrieve application specification"""

    def data_received(self, chunk):
        pass

    def get(self):

        self.write('<h1>specification</h1>')


class api(object):
    """Expose API classes decorator. Setup URI for API class"""

    def __init__(self, *args, **kwargs):

        if 'URI' not in kwargs:
            import inspect
            caller_frame = inspect.stack()[1]
            raise MissingApiRui("Missing uri in API class from module {}".format(caller_frame[1]))

        self.uri = kwargs['URI']
        self.set_api_prefix = False if 'PREFIX' in kwargs and not kwargs['PREFIX'] else True

    def replace_uri_arguments(self):
        _split_url = self.uri.split('/')
        _res = []
        _kw_res = {}
        for s in _split_url:
            _res.append('([^/]+)' if s.startswith(':') else s)
            if s.startswith(':'):
                _kw_res[s[1:]] = _split_url.index(s)

        return '/'.join(_res), _kw_res

    def __call__(self, cls):
        cls.__PATH__ = self.uri
        cls.__URI__, cls.__PATH__PARAMS__ = self.replace_uri_arguments()
        cls.__SET_API_PREFIX__ = self.set_api_prefix

        return cls


class params(object):
    """Examine API call parameters"""

    def __init__(self, *args):
        self.params = args

    @staticmethod
    def convert_arguments(argument, argument_value, argument_type):

        if argument_type == bool:
            try:
                return argument_value.lower() == 'true'
            except AttributeError:
                return isinstance(argument_value, bool) and argument_value

        if argument_type == int:
            if argument_value == '0':
                return 0
            try:
                return int(argument_value)
            except ValueError as e:
                log.critical('Invalid argument {} expected int got {} ({}): {}'.format(
                    argument, argument_value, type(argument_value), e))
                return None

        if argument_type == float:
            try:
                return float(argument_value)
            except ValueError as e:
                log.critical('Invalid argument {} expected float got {} ({}): {}'.format(
                    argument, argument_value, type(argument_value), e))
                return None

        if argument_type == list:
            try:
                el = ast.literal_eval(argument_value)
            except SyntaxError as e:
                log.critical('Invalid argument {} expected list, got {} ({}): {}'.format(
                    argument, argument_value, type(argument_value), e))
                return None

            if type(el) != list:
                log.critical('Invalid argument {} expected list, got {} ({})'.format(
                    argument, argument_value, type(argument_value)))
                return None

            return el

        if argument_type == dict:
            try:
                el = ast.literal_eval(argument)
            except SyntaxError as e:
                log.critical('Invalid argument {} expected dict, got {} ({}): {}'.format(
                    argument, argument_value, type(argument_value), e))
                return None

            if type(el) != dict:
                log.critical('Invalid argument {} expected dict, got {} ({})'.format(
                    argument, argument_value, type(argument_value)))
                return None

            return el

        if argument_type == decimal.Decimal:
            try:
                return decimal.Decimal(argument_value)
            except decimal.InvalidOperation as e:
                log.critical('Invalid argument {} expected Decimal, got {} ({}): {}'.format(
                    argument, argument_value, type(argument_value), e))
                return None

        if argument_type == json:
            try:
                return json.loads(argument_value)
            except json.JSONDecodeError as e:
                log.critical('Invalid argument {} expected json, got {} ({}): {}'.format(
                    argument, argument_value, type(argument_value), e))
                return None

        if argument_type == 'e-mail':

            if '@' not in argument_value:
                log.critical('Invalid argument {} expected email, got {} ({}): {}'.format(
                    argument, argument_value, type(argument_value), 'not an e-mail'))
                return None

        if argument_type == datetime.datetime:
            try:
                return datetime.datetime.strptime(argument_value, "%Y-%m-%d %H:%M:%S")
            except ValueError as e:
                log.critical('Invalid argument {} expected datetime, got {} ({}): {}'.format(
                    argument, argument_value, type(argument_value), e))
                return None

        if argument_type == datetime.date:
            try:
                return datetime.datetime.strptime(argument_value, "%Y-%m-%d")
            except ValueError as e:
                log.critical('Invalid argument {} expected date, got {} ({}): {}'.format(
                    argument, argument_value, type(argument_value), e))
                return None

        return argument_value

    @staticmethod
    def params_type_for_compare(_param_type):
        if _param_type in [int, float, decimal.Decimal, datetime.date, datetime.datetime]:
            return True
        return False

    @staticmethod
    def param_is_lower_then_min(_param_type, _param_value, _param_min_value):

        if not params.params_type_for_compare(_param_type):
            return True
        if _param_value < _param_min_value:
            return False
        return True

    @staticmethod
    def param_is_greater_then_max(_param_type, _param_value, _param_max_value):

        if not params.params_type_for_compare(_param_type):
            return True
        if _param_value > _param_max_value:
            return False
        return True

    def __call__(self, _f):

        @wraps(_f)
        def wrapper(_origin_self, *args, **kwargs):

            _arguments = []

            for _param in self.params:

                _argument = _param['name'].strip()
                _param_type = _param['type']
                _default_param_value = _param['default'] if 'default' in _param else None
                _param_required = _param['required'] if 'required' in _param else True
                _param_min_value = _param['min'] if 'min' in _param else None
                _param_max_value = _param['max'] if 'max' in _param else None

                if _argument in _origin_self.__PATH__PARAMS__:
                    _param_value = _origin_self.request.uri.split('?')[0].split('/')[
                                                                            _origin_self.__PATH__PARAMS__[_argument]]
                    _param_required = True
                else:
                    _param_value = _origin_self.get_argument(_argument, default=_default_param_value)

                if _param_value is None and _param_required:
                    log.critical('Missing required parameter {}'.format(_argument))
                    return _origin_self.error(msgs.MISSING_REQUEST_ARGUMENT)

                _param_converted = params.convert_arguments(_argument, _param_value, _param_type)
                if _param_converted is None:
                    log.critical('Invalid parameter {}'.format(_argument))
                    return _origin_self.error(msgs.MISSING_REQUEST_ARGUMENT)

                if _param_min_value and not params.param_is_lower_then_min(_param_type, _param_converted, _param_min_value):
                    log.warning('{} value {} is lower then required minimum {}'.format(
                        _argument, _param_value, _param_min_value))
                    return _origin_self.error(msgs.ARGUMENT_LOWER_THEN_MINIMUM)

                if _param_max_value and not params.param_is_greater_then_max(_param_type, _param_converted, _param_max_value):
                    log.warning('{} value {} is greater then required maximum {}'.format(
                        _argument, _param_value, _param_min_value))
                    return _origin_self.error(msgs.ARGUMENT_HIGHER_THEN_MINIMUM)

                _arguments.append(_param_converted)

            return _f(_origin_self, *_arguments, **kwargs)

        return wrapper


class DefaultRouteHandler(Base):
    """Base default route handler"""

    def _dummy(self):
        method = self.request.method
        path = self.request.path

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
        self.render('templates/introduction.html')

