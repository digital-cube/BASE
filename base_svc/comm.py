
import json
import urllib
import tornado.web
import tornado.ioloop
import tornado.template
from tornado import gen
from tornado import httpclient

import base_common.msg
import base_config.settings as csettings
import base_lookup.api_messages as amsgs
from base_lookup.http_methods import GET, POST, PUT, DELETE, PATCH
from base_lookup.http_methods import rev as http_rev_map
from base_lookup.http_methods import map as http_map
from base_api.apisvc.apisvc import get_api_specification
from base_config.service import log

_c = 0


class BaseAPIRequestHandler:
    r_ip = "127.0.0.1"

    def __init__(self):
        self._map = {}

    def set_argument(self, key, value):
        self._map[key] = value

    def get_argument(self, key, default='__DEFAULT_VALUE__'):
        if key not in self._map and default != '__DEFAULT_VALUE__':
            return default

        return self._map[key]


def call(svc_url, port, location, data, method, request_timeout=10, force_json=False, call_headers=None):
    import http.client
    conn = http.client.HTTPConnection(svc_url, port)

    if force_json:
        body = json.dumps(data)
        _headers = {'content-type': 'application/json'}
    else:
        body = urllib.parse.urlencode(data)
        _headers = {'content-type': 'application/x-www-form-urlencoded'}

    if call_headers:
        _headers.update(call_headers)

    conn.request(method, "/" + location, body, headers=_headers)

    response = conn.getresponse()
    return response.read().decode('utf-8'), response.status


class MainHandler(tornado.web.RequestHandler):
    def data_received(self, chunk):
        print('RECEIVED CHUNK', chunk)
        print('RECEIVED CHUNK', type(chunk))

    def get(self):

        if self.request.host.startswith('api.') or 'spec' in self.request.uri:

            html = self.get_argument('html', default=False)

            applist = get_api_specification(self)

            if html:
                j = json.loads(applist);

                base = None
                app = None

                for base_key in j['applications'].keys():
                    if base_key == 'BASE':
                        base = j['applications']['BASE']
                        version = j['api_version']
                        base_ordered = list(base.keys())
                        base_ordered .sort()

                    else:
                        app = j['applications'][base_key]

                        app_ordered = list(app.keys())
                        app_ordered.sort()

                        _name = base_key
                        version = app['APP_VERSION'] if 'APP_VERSION' in app else ''


                self.render('apisvctemplate.html', items=[{'name': 'BASE',
                                              'data': base,
                                              'order': base_ordered,
                                              'version': version},
                                             {'name': _name,
                                              'data': app,
                                              'order': app_ordered,
                                              'version': version}])
                return

            self.write(applist)
        else:
            self.write("<h1>Hello! You're doing well</h1>")

    def write_error(self, status_code, **kwargs):
        if not csettings.DEBUG:
            if status_code in [403, 404, 500, 502]:
                self.write('Not implemented')


class GeneralPostHandler(tornado.web.RequestHandler):

    def __init__(self, application, request, **kwargs):
        self.auth_token = None
        self.apimodule_map = None
        self.apimodule = None
        self.api_module_name = None
        self.allowed = None
        self.denied = None
        self.r_ip = None
        self._a_p = None
        super().__init__(application, request, **kwargs)

        if csettings.LB:
            setattr(GeneralPostHandler, 'get', self.a_get)
            setattr(GeneralPostHandler, 'put', self.a_put)
            setattr(GeneralPostHandler, 'post', self.a_post)
            setattr(GeneralPostHandler, 'patch', self.a_patch)
            setattr(GeneralPostHandler, 'delete', self.a_delete)
        else:
            setattr(GeneralPostHandler, 'get', self._get)
            setattr(GeneralPostHandler, 'put', self._put)
            setattr(GeneralPostHandler, 'post', self._post)
            setattr(GeneralPostHandler, 'patch', self._patch)
            setattr(GeneralPostHandler, 'delete', self._delete)

        self.e_msgs = {
            GET: amsgs.NOT_IMPLEMENTED_GET,
            PUT: amsgs.NOT_IMPLEMENTED_PUT,
            POST: amsgs.NOT_IMPLEMENTED_POST,
            PATCH: amsgs.NOT_IMPLEMENTED_PATCH,
            DELETE: amsgs.NOT_IMPLEMENTED_DELETE,
        }

    def data_received(self, chunk):
        print('RECEIVED CHUNK', chunk)
        print('RECEIVED CHUNK', type(chunk))

    def initialize(self, apimodule_map, allowed=None, denied=None):

        self.apimodule_map = apimodule_map
        self.apimodule = self.apimodule_map['module']
        self.api_module_name = self.apimodule.name
        self.allowed = allowed
        self.denied = denied
        log.info(self.api_module_name)

    def write_error(self, status_code, **kwargs):
        if not csettings.DEBUG:
            if status_code in [403, 404, 500, 502]:
                self.write('Not implemented')

    def not_allowed(self):
        self.set_status(405)
        self.finish('Not Allowed')

    def options(self, *args, **kwargs):

        self.set_status(200)
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Methods', 'POST, PUT, PATCH, GET, DELETE, OPTIONS')
        self.set_header('Access-Control-Max-Age', 1000)
        self.set_header('Access-Control-Allow-Headers', 'Origin, X-CSRFToken, Content-Type, Accept, Authorization')
        self.finish('OK')

    @tornado.web.asynchronous
    def a_get(self):

        self.call_api_fun(GET)

    def _get(self):

        self.call_api_fun(GET)

    @tornado.web.asynchronous
    def a_put(self):

        self.call_api_fun(PUT)

    def _put(self):

        self.call_api_fun(PUT)

    @tornado.web.asynchronous
    def a_patch(self):

        self.call_api_fun(PATCH)

    def _patch(self):

        self.call_api_fun(PATCH)

    @tornado.web.asynchronous
    def a_post(self):

        self.call_api_fun(POST)

    def _post(self):

        self.call_api_fun(POST)

    @tornado.web.asynchronous
    def a_delete(self):

        self.call_api_fun(DELETE)

    def _delete(self):

        self.call_api_fun(DELETE)

    def check(self):

        j = {}
        if self.get_secure_cookie("sess_logged_user"):
            sess_logged_user = self.get_secure_cookie("sess_logged_user").decode('utf-8')
            j = json.loads(sess_logged_user)

        ip = '127.0.0.1'

        if 'X-Forwarded-For' in self.request.headers:
            ip = self.request.headers['X-Forwarded-For']

        tk = None
        if 'Authorization' in self.request.headers:
            tka = self.request.headers.get('Authorization')
            tka = tka.split(' ')
            if len(tka) == 1:
                tk = tka[0].strip()

        self.auth_token = tk
        self.r_ip = ip

        return j, ip

    @gen.coroutine
    def a_call(self, _server_ip, method):

        _aclient = httpclient.AsyncHTTPClient(force_instance=True)
        _uri = 'http://{}{}'.format(_server_ip, self.request.uri)
        _body = self.request.body if method not in [GET,] else None

        _headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        if self.auth_token:
            _headers['Authorization'] = self.auth_token

        _res = yield _aclient.fetch(_uri, body=_body, method=http_rev_map[method], headers=_headers)

        # log.info('EXITING SERVER: {}'.format(self._a_p))
        self.write(_res.body.decode('utf-8'))
        self.finish()

    def set_api_header(self, return_type):

        if return_type == 'html':
            self.set_header('Content-Type', 'text/html')

    def call_api_fun(self, method):

        self.set_header('Access-Control-Allow-Origin', '*')

        j, ip = self.check()

        try:
            if method in self.apimodule_map:

                fun = self.apimodule_map[method]

                if hasattr(fun,'__api_return_type__'):
                    self.set_api_header(getattr(fun,'__api_return_type__'))
                else:
                    self.set_header('Content-Type', 'application/json')

                if not hasattr(fun, '__api_method_call__') or not fun.__api_method_call__:
                    self.set_status(500)
                    self.write(json.dumps(base_common.msg.error(amsgs.NOT_API_CALL)))
                    return

                # k = fun.__name__
                # p = fun.__parent__
                _fun_method = getattr(fun, '__api_method_type__')
                _fun_method = http_map[_fun_method]
                if method != _fun_method:
                    log.critical('Trying to call {} method on {} function from {}'.format(
                        method, fun.__name__, self.apimodule.__name__))

                    self.set_status(500)
                    self.write(json.dumps(base_common.msg.error(self.e_msgs[method])))
                    return

                if csettings.LB:

                    global _c
                    _server = csettings.BALANCE[ _c % len(csettings.BALANCE) ]
                    _c += 1

                    self._a_p = _server[-4:]
                    log.info('CALLING SERVER: {}'.format(self._a_p))
                    self.a_call(_server, method)
                    return

                else:

                    result = fun(request_handler=self, logged_user_dict=j, r_ip=ip, auth_token=self.auth_token)

                self.set_status(200)
                if 'http_status' in result:
                    self.set_status(result['http_status'])
                    del result['http_status']

                if result != {}:
                    self.write(json.dumps(result))

            else:
                log.error("ip: {}, {} not implemented".format(ip, http_rev_map[method]))
                self.set_status(404)
                self.set_header('Content-Type', 'application/json')
                self.write(json.dumps(base_common.msg.error(self.e_msgs[method])))

        except Exception as e:

            log.error(
                "ip: {}, module: {}, function: {}, exception: e:{}".format(ip, self.apimodule.__name__, method, e))
            self.set_status(500)
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(base_common.msg.error(e)))
