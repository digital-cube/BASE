# coding= utf-8

import os
import abc
import json
import tornado.web

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

    def __call__(self, cls):
        cls.__URI__ = self.uri
        cls.__SET_API_PREFIX__ = self.set_api_prefix
        return cls


class params(object):
    """Examine API call parameters"""


class DefaultRouteHandler(Base):
    """Base default route handler"""

    def _dummy(self):
        method = self.request.method
        path = self.request.path
        ip = self.request.remote_ip
        self.set_status(404)
        log.warning('trying to call not allowed {} method on {} uri from {}'.format(method, path, ip))
        if method == 'POST':
            return self.error(msgs.POST_NOT_ALLOWED)
        if method == 'PUT':
            return self.error(msgs.PUT_NOT_ALLOWED)
        if method == 'PATCH':
            return self.error(msgs.PATCH_NOT_ALLOWED)
        if method == 'DELETE':
            return self.error(msgs.DELETE_NOT_ALLOWED)
        return self.error(msgs.GET_NOT_ALLOWED)

    def write_error(self, status_code, **kwargs):
        self.write('OVERLOADED ERROR')

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

