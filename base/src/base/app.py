import datetime
import importlib
import json
import logging
import logging.config
import traceback
import uuid
import tortoise
import asyncio
from functools import wraps
from inspect import isclass, signature

from typing import Any

import dateutil.parser
import sqlalchemy.orm.attributes
import tornado.ioloop
import tornado.web
from tornado.httpclient import AsyncHTTPClient

from tortoise import Tortoise

from . import http, token
from .utils.log import log, set_log_context, clear_log_context

LocalOrmModule = None


class NotFoundHandler(tornado.web.RequestHandler):
    def prepare(self):
        self.write(json.dumps({'message': 'invalid URI'}))
        self.set_status(http.status.NOT_FOUND)

    def get(self):
        pass

    def post(self):
        pass

    def put(self):
        pass

    def patch(self):
        pass

    def delete(self):
        pass


class Base(tornado.web.RequestHandler):
    logger = None
    _id_message: str = None
    _message: str = None

    from typing import Optional, Awaitable

    def data_received(self, chunk: bytes) -> Optional[Awaitable[None]]:
        pass

    def prepare(self) -> Optional[Awaitable[None]]:
        self.settings['serve_traceback'] = False

        """
        If the request came from another Base service, it will have a req_id header which can allow us to track a 
        request chain easily between services.
        
        If there is no req_id header, then we create the request id on this initial Handler and pass it on if necessary.
        """
        self.req_id = str(uuid.uuid4()) if 'req_id' not in self.request.headers else self.request.headers['req_id']

        set_log_context(
            req_id=self.req_id,
            method=self.request.method,
            uri=self.request.uri,
            ip=self.request.remote_ip
        )

        return super().prepare()

    def options(self, *args, **kwargs):
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Methods', 'POST, PUT, PATCH, GET, DELETE, OPTIONS, LINK, UNLINK, LOCK')
        self.set_header('Access-Control-Max-Age', 1000)
        self.set_header('Access-Control-Allow-Headers',
                        'Origin, X-CSRFToken, Content-Type, Accept, Authorization, Cache-Control, jwt')
        self.set_status(200)
        self.finish('OK')

    def set_default_headers(self) -> None:
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Methods', 'POST, PUT, PATCH, GET, DELETE, OPTIONS, LINK, UNLINK, LOCK')
        self.set_header('Access-Control-Max-Age', 1000)
        self.set_header('Access-Control-Allow-Headers',
                        'Origin, X-CSRFToken, Content-Type, Accept, Authorization, Cache-Control, jwt')

    def initialize(self) -> None:
        pass

    def log(self, message: str, level: int = 10) -> None:
        """
        Logs a message into the current request logger with a message and level.

        :param message: Message which will be saved in the logs
        :param level: The level (according to Python spec) of the log message severity
        """

        """Find the caller function of the log method and log it as well (go back one frame essentially) """
        import inspect
        func = inspect.currentframe().f_back.f_code

        set_log_context(
            file=func.co_filename, line=func.co_firstlineno
        )

        """Call the log method from utils which handles the full context and outputting to Loggers"""
        log(
            self.logger,
            level,
            include_context=True,
            message=message,
            status=self.get_status(),
            time_ms=(1000.0 * self.request.request_time())
        )

    def write_error(self, status_code: int, **kwargs: Any) -> None:
        self.set_header('Content-Type', 'application/json; charset=UTF-8')

        # print("WRITE_ERROR", kwargs)

        """Add the request id to the error response for easier debugging and log finding"""
        body = {'id_request': self.req_id}

        """
        Look for the message string we are adding to the Exception object
        
        If it is empty, check the handler for the private attribute _reason which can also have the Exception error message
        """
        if 'message' in kwargs and kwargs['message'] is not None:
            message = kwargs['message']
        else:
            message = self._reason

        """
        Look for the id_message string we are adding to the Exception object
        """
        id_message = self._id_message if self._id_message else None

        body.update({
            'method': self.request.method,
            'uri': self.request.path,
            'code': status_code,
            'message': message,
        })

        for arg in kwargs:
            if arg not in body and arg != 'reason':
                body[arg] = kwargs[arg]

        if id_message is not None:
            body.update({
                'id': id_message
            })

        """Set the exc_info value in logging context for exception logging purposes"""
        import sys
        exc_info = sys.exc_info()
        if exc_info != (None, None, None):
            set_log_context(exc_info=exc_info)

        set_log_context(reason=self._reason, message=message)
        if 'exc_info' in kwargs:
            exc_info = kwargs['exc_info']
            set_log_context(exc_info=exc_info)
            if self.settings.get('serve_traceback'):
                # in debug mode, send a traceback
                trace = '\n'.join(
                    traceback.format_exception(*exc_info))
                body['trace'] = trace
        self.finish(body)

    def log_exception(self, typ, value, tb) -> None:
        if isinstance(value, tornado.web.HTTPError):
            if value.log_message:
                msg = value.log_message % value.args
                log(
                    tornado.log.gen_log,
                    logging.WARNING,
                    status=value.status_code,
                    request_summary=self._request_summary(),
                    message=msg
                )
        else:
            log(
                tornado.log.app_log,
                logging.ERROR,
                message='Uncaught exception',
                request_summary=self._request_summary(),
                request=repr(self.request),
                exc_info=(typ, value, tb)
            )

    @staticmethod
    def log_function(handler: tornado.web.RequestHandler) -> None:
        logger = getattr(handler, 'logger',
                         logging.getLogger('base'))
        if handler.get_status() < 400:
            level = logging.INFO
        elif handler.get_status() < 500:
            level = logging.WARNING
        else:
            level = logging.ERROR

        log(
            logger,
            level,
            include_context=True,
            message='RESPONSE',
            status=handler.get_status(),
            time_ms=(1000.0 * handler.request.request_time())
        )
        clear_log_context()


class api:
    """
    API Decorator used to add Base functionality to the RequestHandler.
    """

    def __init__(self, *args, **kwargs):
        self.skip_db = True if 'db' in kwargs and kwargs['db'] == False else False
        self.raw_output = True if 'raw_output' in kwargs and kwargs['raw_output'] == True else False

        pass

    def __call__(self, funct):

        self.__local_orm_module = None

        if not self.skip_db:

            try:
                global LocalOrmModule
                if not LocalOrmModule:
                    LocalOrmModule = importlib.import_module('orm.orm')
            except Exception as e:
                pass

            try:
                self.__local_orm_module = LocalOrmModule
            except:
                pass

        @wraps(funct)
        async def wrapper(_origin_self, *args, **kwargs):

            try:
                sig = signature(funct)

                kwa = {}

                if not hasattr(_origin_self, 'orm_session'):
                    _origin_self.orm_session = None

                    if self.__local_orm_module:
                        _origin_self.orm_session = self.__local_orm_module.session()

                if str(sig) != '(self)':

                    if _origin_self.request.body:
                        try:
                            body = json.loads(_origin_self.request.body.decode('utf-8'))
                        except:
                            body = _origin_self.request.body
                    else:
                        body = {}

                    _origin_self.body = body

                    # handler_args = _origin_self.get_arguments()

                    arg_pos = -1
                    for p in sig.parameters:
                        if p == 'self':
                            continue

                        pp = sig.parameters[p]

                        passed = False

                        arg_pos += 1

                        value = None
                        if _origin_self.path_args and len(_origin_self.path_args) > arg_pos:
                            passed = True
                            value = _origin_self.path_args[arg_pos]
                            if pp.annotation == int:
                                pass
                            elif pp.annotation == float:
                                pass

                        elif _origin_self.get_arguments(pp.name):
                            passed = True
                            value = _origin_self.get_argument(pp.name)

                        elif pp.name in body:
                            passed = True
                            value = body[pp.name]

                        if passed:
                            if pp.annotation == str and type(value) not in (
                                    str, type(None)):
                                raise http.General4xx(message=f"Invalid datatype, int type is expected for {pp.name}",
                                                      id_message="INVALID_DATA_TYPE")

                            elif pp.annotation == int and not type(value) == int:
                                try:
                                    if '.' in value:
                                        raise http.General4xx(f"Invalid datatype, int type is expected for {pp.name}",
                                                              id_message="INVALID_DATA_TYPE")

                                    value = int(value)
                                except:
                                    raise http.General4xx(f"Invalid datatype, int type is expected for {pp.name}",
                                                          id_message="INVALID_DATA_TYPE")

                            elif pp.annotation == bool:

                                if value in (True, '1', 'true', 't', 'T', 'True', 'yes', 'Yes', 'YES'):
                                    value = True
                                elif value in (False, '0', 'false', 'f', 'F', 'False', 'no', 'No', 'NO'):
                                    value = False
                                elif value in ('None', 'null'):
                                    value = None
                                else:
                                    raise http.General4xx(
                                        message=f"Invalid datatype for type boolean {value} {type(value)}",
                                        id_message="INVALID_DATA_TYPE")

                            elif pp.annotation in (datetime.date, datetime.time, datetime.datetime):

                                try:
                                    value = dateutil.parser.parse(value)
                                    if pp.annotation == datetime.date:
                                        value = value.date()
                                    if pp.annotation == datetime.time:
                                        value = value.time()
                                except:
                                    raise http.General4xx(message=f"Invalid value for date/time field",
                                                          id_message="INVALID_DATA_TYPE")

                            elif pp.annotation == float and not type(value) in (float, int):
                                try:
                                    value = float(value)
                                except:
                                    raise http.General4xx(
                                        message=f"Invalid datatype, float type is expected for {pp.name}",
                                        id_message="INVALID_DATA_TYPE")

                            elif pp.annotation == uuid.UUID and not type(value) == uuid.UUID:
                                try:
                                    value = uuid.UUID(value)
                                except:
                                    raise http.General4xx(
                                        message=f"Invalid datatype, UUID type is expected for {pp.name}",
                                        id_message="INVALID_DATA_TYPE")

                            elif isinstance(pp.annotation, sqlalchemy.orm.attributes.InstrumentedAttribute):

                                cls = pp.annotation.class_
                                scls = str(cls).replace("<class '", '').replace("'>", '')
                                amodul = scls.split('.')
                                modul = '.'.join(amodul[:-1])

                                module = importlib.import_module(modul)

                                cls = getattr(module, amodul[-1])

                                if True:
                                    res = _origin_self.orm_session.query(cls).filter(cls.id == value).one_or_none()

                                    kwa[pp.name] = res

                            elif isinstance(pp.annotation, tortoise.fields.data.Field) and pp.annotation.pk:
                                cls = pp.annotation.model
                                print(cls)

                                scls = str(cls).replace("<class '", '').replace("'>", '')
                                amodul = scls.split('.')
                                modul = '.'.join(amodul[:-1])

                                module = importlib.import_module(modul)

                                cls = getattr(module, amodul[-1])

                                field_name = pp.annotation.model_field_name

                                kwa[pp.name] = await cls.filter(**{field_name: value}).get_or_none()

                            elif type(pp.annotation)!=tuple and issubclass(pp.annotation, tortoise.models.Model):
                                try:
                                    kwa[pp.name] = await pp.annotation(**value)
                                except:
                                    pass

                            # elif issubclass(pp.annotation, sql_base):
                            #     model_class = pp.annotation
                            #
                            #     # ukoliko id_user postoji u modelu, i ukoliko se radi u auth useru, znaci
                            #     # da je user ulogovan, ako neko pokusava da upise id_usera, radi se o upravo ulogovanom
                            #     # korisniku, ovo nije dobro jer se time id_user, rezervise za ovu akciju, sto moze
                            #     # da zezne nekog ko to nema u vidu, takod a treba smisliti nesto bolje
                            #
                            #     if hasattr(model_class, 'id_user') and \
                            #             'id_user' not in value and \
                            #             hasattr(_origin_self, 'id_user'):
                            #         value['id_user'] = _origin_self.id_user
                            #
                            #     try:
                            #
                            #         if hasattr(model_class, 'build'):
                            #             kwa[pp.name] = model_class.build(value)
                            #         else:
                            #             # there is no builder, try to construct class
                            #             kwa[pp.name] = model_class(**value)
                            #     except TypeError as te:
                            #         if 'missing' in str(te) and 'required' in str(te) and 'argument' in str(te):
                            #             kwa[pp.name] = None
                            #         else:
                            #             raise http.HttpInvalidParam(str(te))
                            #     except Exception as e:
                            #         kwa[pp.name] = None
                            #         # _origin_self.write(
                            #         #     json.dumps(
                            #         #         {"message": f"Invalid datatype {pp.annotation} error builiding object"}))
                            #         # _origin_self.set_status(http.status.BAD_REQUEST)


                            elif isinstance(pp.annotation, tuple):
                                cls, attr = pp.annotation
                                kwa[pp.name] = await cls.filter(**{attr: value}).get_or_none()
                                pass

                            elif isinstance(pp.annotation, type(Any)):

                                pass

                        # TODO: ovo sada radi, jer su defaultni argumenti int, str, float, ...
                        # medjutim napravice problem kad defaultni argumenti budu klase, tako da bi trebalo
                        # koristiti nesto poput: isinstance(pp.dafault, inspect._empty) kad se provali kako !

                        if pp.name not in kwa:
                            if isclass(pp.default):

                                # if pp.name not in body:
                                if not passed:

                                    # skip *args and **kwargs
                                    if '*' in str(pp):
                                        continue

                                    _origin_self.write(
                                        json.dumps(
                                            {"message": f"Mandatory argument {pp.name} missing in input request"}, ensure_ascii=False))
                                    _origin_self.set_status(http.status.BAD_REQUEST)
                                    return

                                kwa[pp.name] = value
                            else:

                                if passed:
                                    kwa[pp.name] = value
                                else:
                                    kwa[pp.name] = pp.default

                _args = []

                # try:
                res = await funct(_origin_self, *_args, **kwa)
                # except http.HttpInternalServerError as e:
                #     _origin_self.send_error(e.status(), reason=str(e.message))
                #     raise
                # except Exception as e:
                #     print("EEEE",e)

                status_code = http.status.OK

                response = None

                if type(res) == tuple:
                    response = res[0]
                    status_code = res[1]

                elif type(res) in (dict, list):
                    response = res

                elif isinstance(res, type(None)):
                    response = None
                    status_code = http.status.NO_CONTENT

                else:
                    response = res

                _origin_self.set_status(status_code)

                if response is not None:

                    if self.raw_output:
                        _origin_self.write(response)
                    else:
                        try:
                            _origin_self.set_header('Content-Type', 'application/json; charset=UTF-8')
                            prepared_response = json.dumps(response, ensure_ascii=False)
                            _origin_self.write(prepared_response)
                        except:
                            _origin_self.write(response)

            except http.HttpInvalidParam as e:
                _origin_self._id_message = str(e.id_message)

                kwargs = e._dict()
                # print("KWARG", kwargs)
                _origin_self.send_error(e.status(), reason=str(e.message), **kwargs)

            except http.BaseHttpException as e:
                if _origin_self.orm_session:
                    _origin_self.orm_session.rollback()

                _origin_self._id_message = str(e.id_message)
                _origin_self.send_error(e.status(), reason=str(e.message))

            except Exception as e:
                if _origin_self.orm_session:
                    _origin_self.orm_session.rollback()

                _origin_self._id_message = str(e.id_message) if hasattr(e, 'id_message') else None
                _origin_self.send_error(http.status.INTERNAL_SERVER_ERROR,
                                        reason=str(e.message).split('\n')[0] if hasattr(e, 'message') else None)

            finally:
                if _origin_self.orm_session:
                    _origin_self.orm_session.close()

        return wrapper


class auth:
    def __init__(self, *args, **kwargs):

        self.allowed_flags = kwargs['permissions'] if 'permissions' in kwargs else None

        pass

    def __call__(self, funct):

        try:
            self.__local_orm_module = LocalOrmModule
        except:
            pass

        @wraps(funct)
        async def wrapper(_self_origin, *args, **kwargs):

            if not hasattr(_self_origin, 'orm_session'):
                _self_origin.orm_session = None

                if self.__local_orm_module:
                    _self_origin.orm_session = self.__local_orm_module.session()

            from base import config
            if config.conf['authorization']['key'] in _self_origin.request.headers:

                _token = _self_origin.request.headers[config.conf['authorization']['key']]
                res = token.token2user(_token)

                id_user = res['id_user'] if res and 'id_user' in res else None
                id_session = res['id'] if res and 'id' in res else None

                # ?!? iz nekog razloga je prestalo da sljaka
                # ERROR : Exception after Future was cancelled

                # if not res:
                #     raise http.HttpErrorUnauthorized

                permissions = res['permissions'] if res and 'permissions' in res else None

                _self_origin.permissions = permissions

                if self.allowed_flags is not None:
                    if permissions is not None:
                        # print("PROVERAVAM PERMISSIONS", "permissions:", permissions, "self.allowed_flags:",
                        #       self.allowed_flags, "|:", permissions | self.allowed_flags, "&:",
                        #       permissions & self.allowed_flags)
                        if permissions & self.allowed_flags == 0:
                            _self_origin.set_status(http.status.UNAUTHORIZED)
                            _self_origin.write('{"message":"unauthorized"}')
                            return

                if res:
                    # print("RES",res, 'id_user', id_user)
                    # on user service try to assign user

                    _self_origin.id_user = id_user
                    _self_origin.id_session = id_session

                    _self_origin.user = None

                    # try:
                    #     usermodule = importlib.import_module('orm.models')
                    #     _self_origin.user = _self_origin.orm_session.query(usermodule.User).filter(
                    #         usermodule.User.id == id_user).one_or_none()
                    # except Exception as e:
                    #     _self_origin.user = None

                    await funct(_self_origin, *args, **kwargs)
                    return

            #             _self_origin.set_status(http.status.UNAUTHORIZED)
            #             _self_origin.write('{"message":"unauthorized"}')

            _self_origin.send_error(http.status.UNAUTHORIZED, message='Unauthorized',
                                    id_message='UNAUTHORIZED')

        return wrapper


class auth_tortoise:
    def __init__(self, *args, **kwargs):

        self.allowed_flags = kwargs['permissions'] if 'permissions' in kwargs else None

        pass

    def __call__(self, funct):

        @wraps(funct)
        async def wrapper(_self_origin, *args, **kwargs):

            from base import config
            if config.conf['authorization']['key'] in _self_origin.request.headers:

                _token = _self_origin.request.headers[config.conf['authorization']['key']]
                res = token.token2user(_token)

                id_user = res['id_user'] if res and 'id_user' in res else None
                id_session = res['id'] if res and 'id' in res else None

                # ?!? iz nekog razloga je prestalo da sljaka
                # ERROR : Exception after Future was cancelled

                # if not res:
                #     raise http.HttpErrorUnauthorized

                _self_origin.id_user = id_user
                _self_origin.id_session = id_session

                await funct(_self_origin, *args, **kwargs)
                return

            _self_origin.send_error(http.status.UNAUTHORIZED, message='Unauthorized',
                                    id_message='UNAUTHORIZED')

        return wrapper


class route:
    uri = []

    @staticmethod
    def all():
        if not hasattr(route, '_handlers'):
            return []
        return getattr(route, '_handlers')

    @staticmethod
    def print_all_routes():
        print("---[", 'routes', "]" + ('-' * 47))
        for r in route.all():
            print("ROUTE", r)

        print("-" * 60)

    @staticmethod
    def set(key, value):

        if not hasattr(route, '_global_settings'):
            route._global_settings = {}

        route._global_settings[key] = value

    @staticmethod
    def get(key, default=None):

        if hasattr(route, '_global_settings'):
            if key in route._global_settings:
                return route._global_settings[key]

        return default

    @staticmethod
    def register_handler(uri, handler):

        if not hasattr(route, '_handlers'):
            route._handlers = []

        if not hasattr(route, '_handler_names'):
            route._handler_names = set()

        for _uri, _ in route._handlers:
            if _uri == uri:
                raise NameError(f"Error creating api, endopoint '{_uri}'  already exists")

        route._handlers.append((uri, handler))

    @staticmethod
    def handlers(readonly=False):
        if hasattr(route, '_handlers'):
            return sorted(route._handlers, reverse=True)

        return []

    @staticmethod
    def handler_names():
        if hasattr(route, '_handler_names'):
            return route._handler_names

        return set()

    @staticmethod
    def set_handler_names(hn):
        route._handler_names = hn

    def __init__(self, URI='/?', *args, **kwargs):

        self.uri = []

        uris = [URI] if type(URI) == str else URI

        specified_prefix = kwargs['PREFIX'] if 'PREFIX' in kwargs else None

        for uri in uris:
            parts = uri.split('/')
            rparts = []
            for p in parts:
                rparts.append("([^/]*)" if len(p) and p[0] == ':' else p)

            self.uri.append({'specified_prefix': specified_prefix, 'route': '/'.join(rparts)})

    def __call__(self, cls):

        # print("CLS", cls)

        scls = str(cls).replace("<class '", "").replace("'>", "")
        svc = scls.split('.')

        self.handler_name = svc[-1]

        route_handler_names = route.handler_names()

        if self.handler_name in route_handler_names:
            raise NameError(f"Handler with class {self.handler_name} already defined in project, use unique class name")

        route_handler_names.add(self.handler_name)
        route.set_handler_names(route_handler_names)

        # prefix = config.services.prefix if hasattr(config.services, 'prefix') else ''
        #
        # if svc[0] == 'services' and len(svc) > 2:
        #     svc_name = svc[1]
        #
        #     scfg = config.services.svc(svc_name)
        #     if 'api' in scfg and 'prefix' in scfg['api']:
        #         prefix += scfg['api']['prefix']

        # from base import registry
        # prefix = registry.prefix()
        # print('prefix:',prefix)

        # prefix = ''

        prefix = route.get('prefix', '')
        # print('pfx', prefix)
        # prefix = '' if not hasattr(route, '_prefix') else route._prefix

        for duri in self.uri:
            uri = duri['route']
            default_prefix = prefix + ('/' if len(uri) > 0 and uri[0] != '/' else '')
            if duri['specified_prefix'] is not None:
                default_prefix = duri['specified_prefix'].strip()
                # if len(default_prefix) and default_prefix[-1] != '/':
                #     default_prefix += '/'

            furi = default_prefix + uri

            furi = furi.strip()
            if furi[-1] == '/':
                furi += '?'
            elif furi[-1] != '?':
                furi += '/?'

            route.register_handler(furi, cls)
        return cls


async def depricated_IPC(request, service: str, method: str, relative_uri: str, body: dict = None, abs_uri: str = None):
    from . import registry

    if registry.registered(service):
        http_client = AsyncHTTPClient()

        if abs_uri:
            uri = f'{registry.address(service)}{abs_uri}'
        else:
            uri = f'{registry.address(service)}{registry.prefix(service)}{relative_uri}'
        method = method.upper()
        headers = {}

        from base import config
        if request and request.headers and config.conf['authorization']['key'] in request.headers:
            headers[config.conf['authorization']['key']] = request.headers[config.conf['authorization']['key']]

        try:
            _body = None if method in ('GET', 'DELETE') else json.dumps(body, ensure_ascii=False)
            # print(f"IPC URI on service {service}", uri)
            result = await http_client.fetch(uri, method=method, headers=headers, body=_body)
            # print("RES", result)
            # print("_"*100)
        except Exception as e:
            msg = str(e)
            try:
                msg = json.loads(e.response.body.decode('utf-8'))
            except:
                pass
            return False, msg

        return True, json.loads(result.body) if result.body else None

    return False, f"Service {service} is not registered"


def make_app(**kwargs):
    debug = True
    default_handler_class = NotFoundHandler

    if 'default_handler_class' in kwargs:
        default_handler_class = kwargs['default_handler_class']

    if 'debug' in kwargs:
        debug = kwargs['debug']

    readonly = kwargs['readonly'] if 'readonly' in kwargs else False

    from base import config
    config.init_logging()

    return tornado.web.Application(route.handlers(readonly=readonly),
                                   debug=debug,
                                   default_handler_class=default_handler_class,
                                   log_function=Base.log_function)


async def init_orm():
    from base import config

    await Tortoise.init(
        config=config.tortoise_config()
    )


def run(**kwargs):
    from base import config

    if 'port' in kwargs:
        port = kwargs['port']
    else:
        port = config.conf['port'] if 'port' in config.conf else 9000

    app = make_app(**kwargs)
    print(f'listening on port {port}')
    app.listen(port)
    loops = tornado.ioloop.IOLoop.current()
    loops.run_sync(init_orm)

    route.print_all_routes()

    try:
        loops.start()
    finally:
        asyncio.get_event_loop().run_until_complete(Tortoise.close_connections())
