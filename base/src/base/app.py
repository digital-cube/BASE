import os
import sys
import json
import uuid
import inspect
import logging
import asyncio
import tortoise
import argparse
import datetime
import traceback
import importlib
import tornado.web
import tornado.ioloop
import logging.config
import dateutil.parser
# import sqlalchemy.orm.attributes

from typing import Any
from functools import wraps
from tortoise import Tortoise
from typing import Optional, Awaitable
from inspect import isclass, signature
from tornado.httpclient import AsyncHTTPClient

from . import http, token
from .utils.log import log, set_log_context, clear_log_context, message_from_context, get_log_context
from .lookup.scope_permissions import WRITE, READ

LocalOrmModule = None
base_logger = logging.getLogger('base')


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


    def data_received(self, chunk: bytes) -> Optional[Awaitable[None]]:
        pass

    def prepare(self) -> Optional[Awaitable[None]]:
        self.settings['serve_traceback'] = False

        # If the request came from another Base service, it will have a req_id header which can allow us to track a
        # request chain easily between services.
        #
        # If there is no req_id header, then we create the request id on this initial Handler and pass it on if necessary.
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

        # Find the caller function of the log method and log it as well (go back one frame essentially)
        func = inspect.currentframe().f_back.f_code

        set_log_context(
            file=func.co_filename, line=func.co_firstlineno
        )

        # Call the log method from utils which handles the full context and outputting to Loggers
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

        # Add the request id to the error response for easier debugging and log finding
        body = {'id_request': self.req_id}

        # Look for the message string we are adding to the Exception object
        #
        # If it is empty, check the handler for the private attribute _reason which can also have the Exception error message
        if 'message' in kwargs and kwargs['message'] is not None:
            message = kwargs['message']
        else:
            message = self._reason

        # Look for the id_message string we are adding to the Exception object
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

        # Set the exc_info value in logging context for exception logging purposes
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
        from base import config
        if not config.conf['verbose']:
            _message = message_from_context()
            base_logger.critical(_message)
            return

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

        from base import config
        if not config.conf['verbose']:
            # stop logging every call except it is an exception
            context = get_log_context()
            if 'exc_info' in context:
                _message = message_from_context()
                base_logger.critical(_message)
            return

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

                            elif pp.annotation == dict:
                                if type(value) != dict:
                                    if type(value) == str:
                                        try:
                                            value = json.loads(value)
                                        except json.JSONDecodeError as e:
                                            base_logger.error(f'Can not load dict from string -> {value}: {e}')
                                            raise http.General4xx(
                                                message=f"Invalid data type {type(value)} for {value}",
                                                id_message="INVALID_DATA_TYPE")

                                    else:
                                        base_logger.error(f'Can not cast to dict type {type(value)} value {value}')
                                        raise http.General4xx(
                                            message=f"Invalid data type {type(value)} for {value}",
                                            id_message="INVALID_DATA_TYPE")
                                # else do nothing with the value

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

                            # elif isinstance(pp.annotation, sqlalchemy.orm.attributes.InstrumentedAttribute):
                            #
                            #     cls = pp.annotation.class_
                            #     scls = str(cls).replace("<class '", '').replace("'>", '')
                            #     amodul = scls.split('.')
                            #     modul = '.'.join(amodul[:-1])
                            #
                            #     module = importlib.import_module(modul)
                            #
                            #     cls = getattr(module, amodul[-1])
                            #
                            #     if True:
                            #         res = _origin_self.orm_session.query(cls).filter(cls.id == value).one_or_none()
                            #
                            #         kwa[pp.name] = res

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

                            elif not isinstance(pp.annotation, tuple) and issubclass(pp.annotation, tortoise.models.Model):
                                try:
                                    kwa[pp.name] = await pp.annotation(**value)
                                except Exception as e:
                                    pass

                            elif isinstance(pp.annotation, tuple):
                                cls, attr = pp.annotation
                                try:
                                    _db_item = await cls.filter(**{attr: value}).get_or_none()
                                    if not _db_item:
                                        _cls_name = cls.__name__
                                        base_logger.error(f'Error getting {_cls_name} with {attr} {value}: Item not found')
                                        raise http.HttpErrorNotFound(
                                            message=f"{_cls_name} not found",
                                            id_message="INVALID_DATA")

                                    kwa[pp.name] = _db_item
                                except tortoise.exceptions.OperationalError as e:
                                    _cls_name = cls.__name__
                                    base_logger.error(f'Error getting {_cls_name} with {attr} {value}: {e}')
                                    raise http.General4xx(
                                        message=f"Invalid data {value} for {attr} {_cls_name} or {_cls_name} not found",
                                        id_message="INVALID_DATA_TYPE")

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
                                            {"message": f"Mandatory argument {pp.name} missing in input request"},
                                            ensure_ascii=False))
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
                            prepared_response = json.dumps(response, ensure_ascii=False, default=lambda o: str(o))
                            _origin_self.write(prepared_response)
                        except:
                            _origin_self.write(response)

            except http.HttpInvalidParam as e:
                _origin_self._id_message = str(e.id_message)

                kwargs = e._dict()
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

                if not res:
                    _self_origin.set_status(http.status.UNAUTHORIZED)
                    _self_origin.write('{"message":"unauthorized"}')
                    return

                id_user = res['id_user'] if res and 'id_user' in res else None
                user = res['user']
                id_session = res['id'] if res and 'id' in res else None
                id_tenant = res['id_tenant'] if res and 'id_tenant' in res else None
                id_groups = res['id_groups'] if res and 'id_groups' in res else None

                if 'scope_id' in config.conf and config.conf['scope_id']:
                    if 'scopes' not in user or not user['scopes'] or config.conf['scope_id'] not in user['scopes']:
                        base_logger.error(f'User {user["id"]} scopes {user["scopes"]} not match for service {config.conf["name"]} scope {config.conf["scope_id"]}')
                        _self_origin.set_status(http.status.UNAUTHORIZED)
                        _self_origin.write('{"message":"unauthorized"}')
                        return

                    user_scope_permissions = user['scopes'][config.conf['scope_id']]
                    if not bool(user_scope_permissions & WRITE) and funct.__name__ != 'get':
                        base_logger.error(f'User {user["id"]} scopes {user["scopes"]} are insufficient for {funct}')
                        _self_origin.set_status(http.status.UNAUTHORIZED)
                        _self_origin.write('{"message":"unauthorized"}')
                        return
                    if not bool(user_scope_permissions & READ) and funct.__name__ == 'get':
                        base_logger.error(f'User {user["id"]} scopes {user["scopes"]} are insufficient for {funct}')
                        _self_origin.set_status(http.status.UNAUTHORIZED)
                        _self_origin.write('{"message":"unauthorized"}')
                        return

                permissions = res['permissions'] if res and 'permissions' in res else None

                _self_origin.permissions = permissions

                if self.allowed_flags is not None:
                    if permissions is not None:
                        if permissions & self.allowed_flags == 0:
                            _self_origin.set_status(http.status.UNAUTHORIZED)
                            _self_origin.write('{"message":"unauthorized"}')
                            return

                if res:
                    # on user service try to assign user

                    _self_origin.id_user = id_user
                    _self_origin.user = user
                    _self_origin.id_session = id_session
                    _self_origin.id_tenant = id_tenant
                    _self_origin.id_groups = id_groups

                    return await funct(_self_origin, *args, **kwargs)

            _self_origin.send_error(http.status.UNAUTHORIZED, message='Unauthorized',
                                    id_message='UNAUTHORIZED')
        return wrapper


class api_auth:

    def __call__(self, funct):

        @wraps(funct)
        async def wrapper(_self_origin, *args, **kwargs):

            from base import config
            _authorization_key_name = config.conf['authorization']['api_key_header_name'] if 'api_key_header_name' in config.conf['authorization'] else None
            _authorization_key = config.conf['authorization']['api_key'] if 'api_key' in config.conf['authorization'] else None
            if not _authorization_key_name:
                base_logger.critical('Missing api authorization header name in configuration, set "api_key_header_name"')
                _self_origin.set_status(http.status.UNAUTHORIZED)
                _self_origin.write('{"message":"unauthorized"}')
                return

            if not _authorization_key:
                base_logger.critical('Missing api key in configuration, set: "api_key"')
                _self_origin.set_status(http.status.UNAUTHORIZED)
                _self_origin.write('{"message":"unauthorized"}')
                return

            _header_api_key = _self_origin.request.headers.get(_authorization_key_name)
            if _header_api_key != _authorization_key:
                base_logger.error(f'Invalid {_authorization_key_name}: {_header_api_key}')
                _self_origin.set_status(http.status.UNAUTHORIZED)
                _self_origin.write('{"message":"unauthorized"}')
                return


            return await funct(_self_origin, *args, **kwargs)

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
        print("---[", 'routes', "]" + ('-' * 77))
        for r in route.all():
            print("ROUTE", r)

        print("-" * 90)

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
    def register_handler(uri, handler, properties=None):

        if not hasattr(route, '_handlers'):
            route._handlers = []

        if not hasattr(route, '_handler_names'):
            route._handler_names = set()

        for _uri, *_ in route._handlers:
            if _uri == uri:
                raise NameError(f"Error creating api, endopoint '{_uri}'  already exists")

        if not properties:
            route._handlers.append((uri, handler))
        else:
            route._handlers.append((uri, handler, properties))

    @staticmethod
    def register_static_handler(uri, static_path):

        if not hasattr(route, '_handlers'):
            route._handlers = []

        if not hasattr(route, '_handler_names'):
            route._handler_names = set()

        for _uri, *_ in route._handlers:
            if _uri == uri:
                raise NameError(f"Error creating api, endopoint '{_uri}'  already exists")

        route._handlers.append((uri, tornado.web.StaticFileHandler, {'path': static_path}))

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

        # if not specified_prefix:
        #     from base import config
        #     specified_prefix = config.conf['prefix']

        for uri in uris:
            parts = uri.split('/')
            rparts = []
            for p in parts:
                rparts.append("([^/]*)" if len(p) and p[0] == ':' else p)

            self.uri.append({'specified_prefix': specified_prefix, 'route': '/'.join(rparts)})

    def __call__(self, cls):

        scls = str(cls).replace("<class '", "").replace("'>", "")
        svc = scls.split('.')

        self.handler_name = svc[-1]

        route_handler_names = route.handler_names()

        if self.handler_name in route_handler_names:
            raise NameError(f"Handler with class {self.handler_name} already defined in project, use unique class name")

        route_handler_names.add(self.handler_name)
        route.set_handler_names(route_handler_names)

        prefix = route.get('prefix', '')

        for duri in self.uri:
            uri = duri['route']
            default_prefix = prefix + ('/' if len(uri) > 0 and uri[0] != '/' else '')
            if duri['specified_prefix'] is not None:
                default_prefix = duri['specified_prefix'].strip()

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
            result = await http_client.fetch(uri, method=method, headers=headers, body=_body)
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
    _tronado_settings = config.conf['tornado_settings']
    if 'static_paths' in config.conf and config.conf['static_paths']:
        for _static in config.conf['static_paths']:
            _root_dir = sys.path[0]
            route.register_static_handler(f'{_static[0]}/(.*)', f'{_root_dir}{_static[1]}')

    # present all api modules
    for api_module in config.conf['APIs']:
        importlib.import_module(api_module)

    return tornado.web.Application(
        route.handlers(readonly=readonly),
        debug=debug,
        default_handler_class=default_handler_class,
        log_function=Base.log_function,
        **_tronado_settings
    )


async def init_orm():
    from base import config

    await Tortoise.init(
        config=config.tortoise_config()
    )


def get_the_caller():
    '''
    Returns a dictionary with information about the running top level Python
    script:
    ---------------------------------------------------------------------------
    dir:    directory containing script or compiled executable
    name:   name of script or executable
    source: name of source code file
    ---------------------------------------------------------------------------
    "name" and "source" are identical if and only if running interpreted code.
    When running code compiled by py2exe or cx_freeze, "source" contains
    the name of the originating Python script.
    If compiled by PyInstaller, "source" contains no meaningful information.
    
    ============================================================================
    from :

    https://code.activestate.com/recipes/579018-python-determine-name-and-directory-of-the-top-lev/

    MIT Licence
    '''

    # ---------------------------------------------------------------------------
    # scan through call stack for caller information
    # ---------------------------------------------------------------------------
    for teil in inspect.stack():
        # skip system calls
        if teil[1].startswith("<"):
            continue
        if teil[1].upper().startswith(sys.exec_prefix.upper()):
            continue
        trc = teil[1]

    # trc contains highest level calling script name
    # check if we have been compiled
    if getattr(sys, 'frozen', False):
        scriptdir, scriptname = os.path.split(sys.executable)
        return {"dir": scriptdir,
                "name": scriptname,
                "source": trc}

    # from here on, we are in the interpreted case
    scriptdir, trc = os.path.split(trc)
    # if trc did not contain directory information,
    # the current working directory is what we need
    if not scriptdir:
        scriptdir = os.getcwd()

    scr_dict = {"name": trc,
                "source": trc,
                "dir": scriptdir}
    return scr_dict

def parse_arguments(**kwargs):

    from base import config
    from base import __VERSION__
    _app_name = get_the_caller()['name'] if config.conf["default_config"] else config.conf['name']
    _app_port = kwargs['port'] if 'port' in kwargs else config.conf['port'] if 'port' in config.conf else 9000

    argument_parser = argparse.ArgumentParser(prog=_app_name or os.getcwd())
    argument_parser.add_argument('-p', '--port', default=_app_port, help='Application port')
    argument_parser.add_argument('-V', '--verbose', help='Run application with more verbose output', action='store_true')
    argument_parser.add_argument('-v', '--version', action='version',
                                 version=f'{_app_name} v{config.conf["app_version"]} (base3 v{__VERSION__})',
                                 help='Print app version and exit')
    _args = argument_parser.parse_args()
    _args.prog = argument_parser.prog
    return _args

def run(**kwargs):
    import base
    from base import config
    args = parse_arguments(**kwargs)
    if args.verbose:
        config.conf['verboase'] = args.verbose

    app = make_app(**kwargs)

    if 'print_app_info' in kwargs and kwargs['print_app_info']:
        print(f'{args.prog} listen on port {args.port}: http://{config.conf["host"]}:{args.port}{kwargs["about"] if "about" in kwargs else ""}')

    if 'print_routes' in kwargs and kwargs['print_routes']:
        base.route.print_all_routes()

    app.listen(args.port)
    loops = tornado.ioloop.IOLoop.current()

    if config.conf["use_database"]:
        loops.run_sync(init_orm)

    if args.verbose:
        route.print_all_routes()

    try:
        loops.start()
    finally:
        asyncio.get_event_loop().run_until_complete(Tortoise.close_connections())
