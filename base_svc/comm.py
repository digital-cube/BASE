import urllib

import json
import tornado.ioloop
import tornado.template
import tornado.web
# from tornado import httpclient

import base_common.msg
import base_config.settings as csettings
from base_lookup.http_methods import GET, POST, PUT, DELETE, PATCH
from base_lookup.http_methods import rev as http_rev_map
from base_lookup.methods_mapping import method_map
from base_lookup.methods_mapping import method_map_rev
from base_api.apisvc.apisvc import get_api_specification


class BaseAPIRequestHandler:
    r_ip = "127.0.0.1"

    def __init__(self, logfile):
        self._map = {}
        self.log = logfile

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

                for key in j['applications'].keys():
                    if key == 'BASE':
                        base = j['applications']['BASE']
                        version = j['api_version']
                        base_ordered = list(base.keys())
                        base_ordered .sort()

                    else:
                        app = j['applications'][key]

                        app_ordered = list(app.keys())
                        app_ordered.sort()

                        name = key
                        version = j['api_version']

                self.render('x.html', items=[{'name': 'BASE',
                                              'data': base,
                                              'order': base_ordered,
                                              'version': version},
                                             {'name': name,
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
        self.apimodule = None
        self.name = None
        self.allowed = None
        self.denied = None
        self.log = None
        self.r_ip = None
        super().__init__(application, request, **kwargs)

    def data_received(self, chunk):
        print('RECEIVED CHUNK', chunk)
        print('RECEIVED CHUNK', type(chunk))

    def initialize(self, apimodule, log, allowed=None, denied=None):

        self.apimodule = apimodule
        self.name = apimodule.name
        self.allowed = allowed
        self.denied = denied
        self.log = log
        self.log.info(self.name)

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
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.set_header('Access-Control-Max-Age', 1000)
        self.set_header('Access-Control-Allow-Headers', 'Origin, X-CSRFToken, Content-Type, Accept, Authorization')
        self.finish('OK')

    def get(self):

        self.call_api_fun(method_map[GET])

    def put(self):

        self.call_api_fun(method_map[PUT])

    def patch(self):

        self.call_api_fun(method_map[PATCH])

    def post(self):

        self.call_api_fun(method_map[POST])

    def delete(self):

        self.call_api_fun(method_map[DELETE])

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

    def call_api_fun(self, method):

        self.set_header('Access-Control-Allow-Origin', '*')

        j, ip = self.check()

        try:
            if hasattr(self.apimodule, method):
                fun = getattr(self.apimodule, method)
                result = fun(self, logged_user_dict=j)

                self.set_status(200)
                if 'http_status' in result:
                    self.set_status(result['http_status'])
                    del result['http_status']

                if result != {}:
                    self.write(json.dumps(result))

            else:
                self.log.error("ip: {}, {} not implemented".format(ip, http_rev_map[method_map_rev[method]]))
                self.set_status(404)
                self.write(json.dumps(
                    base_common.msg.error('{} not implemented'.format(http_rev_map[method_map_rev[method]]))))

        except Exception as e:

            self.log.error(
                "ip: {}, module: {}, function: {}, exception: e:{}".format(ip, self.apimodule.__name__, method, e))
            self.set_status(500)
            self.write(json.dumps(base_common.msg.error(e)))
