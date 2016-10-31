# coding= utf-8

import abc

import tornado.web
from base.application.helpers.exceptions import MissingApiRui


class base(tornado.web.RequestHandler):
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

    def ok(self, *args, **kwargs):
        self.write('<h1>{}</h1>'.format(','.join(args)))

    def error(self, *args, **kwargs):
        self.set_status(400, reason='bad request')


class SpecificationHandler(tornado.web.RequestHandler):

    def data_received(self, chunk):
        pass

    def get(self):

        self.write('<h1>specification</h1>')


class api(object):
    """Expose API classes decorator. Setup URI for API class"""

    def __init__(self, *args, **kwargs):

        if not 'URI' in kwargs:
            import inspect
            caller_frame = inspect.stack()[1]
            raise MissingApiRui("Missing uri in API class from module {}".format(caller_frame[1]))

        self.uri = kwargs['URI']
        self.set_api_prefix = False if 'PREFIX' in kwargs and not kwargs['PREFIX'] else True

    def __call__(self, cls):
        cls.__URI__ = self.uri
        cls.__SET_API_PREFIX__ = self.set_api_prefix
        return cls


@api(URI=r'/')
class BaseHandler(base):

    def _dummy(self):
        return self.ok('dummy request')

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


