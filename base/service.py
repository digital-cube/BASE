
import tornado.web
import tornado.ioloop
import abc
from functools import wraps


# def route(*arguments):
#
#     def original_wrapper(original_f):
#
#         @wraps(original_f)
#         def wrapper(*args, **kwargs):
#
#             return original_f(*args, **kwargs)
#
#         wrapper.__url__ =


class base(tornado.web.RequestHandler):

    __metaclass__ = abc.ABCMeta

    def ok(self, *args, **kwargs):

        self.write('<h1>{}</h1>'.format(','.join(args)))

    def error(self, *args, **kwargs):

        self.set_status(400, reason='bad request')



class MainHandler(base):

    _route = r'^/$'

    def get(self):
        # self.write('get ok')
        import bcrypt

        username = 'd.olinics@gmail.com'
        password = '123'
        print(bcrypt.hashpw('{}{}'.format(username, password).encode('utf-8'), bcrypt.gensalt()).decode('utf-8'))

        return self.ok('main get')

    def post(self):
        # self.write('post ok')
        return self.ok('main post')

class AnotherHandler(base):

    _route = r'^/fuck$'

    def get(self):
        return ok('another handler')


class AnotherHandler2(base):

    _route = r'^/(.*)/this$'

    def get(self,name):
        return ok('another handler 2 {}'.format(name))


class AnotherHandler3(base):

    _route = r'^/(.*)/this/(.*)$'

    def get(self, name, second):
        return ok('another handler 3 {} | {}'.format(name, second))

entries = []


# def build_request_handler(BaseClass):
#
#     class NewClass(tornado.web.RequestHandler): pass
#     NewClass.__name__ = 'base_{}'.format(BaseClass.__name__)
#     return NewClass


# def fill_entries():
#     global entries
#
#     for c in (MainHandler, AnotherHandler, AnotherHandler2, AnotherHandler3):
#         print(type(c), c.__name__)
#         nc = build_request_handler(c)
#         if hasattr(c, 'get'):
#             def g(self)
#             setattr(nc, 'get', c.get)
#
#         print(type(nc), nc.__name__)

entries = [
            (r'^/$', MainHandler),
            # (r'^/fuck$', AnotherHandler),
            # (r'^/(.*)/this$', AnotherHandler2),
            # (r'^/(.*)/this/(.*)$', AnotherHandler3),
        ]


def baserun():
    # fill_entries()

    svc_port = 8001

    app = tornado.web.Application(
        entries,
        debug=True,
        cookie_secret='fuck_this_man'
    )

    print('starting base service on {}: http://localhost:{}'.format(svc_port, svc_port))
    app.listen(svc_port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':

    baserun()
