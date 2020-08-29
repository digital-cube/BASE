import logging
import logging.config
import sys
import os

import tornado.ioloop
import asyncio
import aiotask_context as context
import tornado.web
import json
import uuid
import yaml
from functools import wraps
from inspect import signature
import inspect
import importlib
import sqlalchemy.orm.attributes
from typing import Any

from base import http, token

import base.utils.log as logutils
from base.orm import sql_base

# import config.services

LOGGER_NAME = 'microsvc-base-test'


class BASE(tornado.web.RequestHandler):

    def prepare(self):
        self.req_id = str(uuid.uuid4()) if 'req_id' not in self.request.headers else self.request.headers['req_id']

        logutils.set_log_context(
            req_id=self.req_id,
            method=self.request.method,
            uri=self.request.uri,
            ip=self.request.remote_ip
        )

        return super().prepare()

    def initialize(self, logger=None):
        if not logger:
            full_path = os.path.realpath(__file__)
            my_dir_name = os.path.dirname(full_path)

            with open(my_dir_name + '/config/logs.yaml') as file:
                log_config = yaml.load(file, Loader=yaml.SafeLoader)
                logging.config.dictConfig(log_config['logging'])
                logger = logging.getLogger(LOGGER_NAME)

        self.logger = logger


class develgen:

    def __init__(self, *args, **kwargs):
        # print("develgen - init")
        pass

    def __call__(self, funct):
        # print('develgen - call')
        return funct


class api:

    # TODO: WEAK:boolean = False

    def __init__(self, *args, **kwargs):
        self.skip_db = True if 'db' in kwargs and kwargs['db'] == False else False

        pass

    def __call__(self, funct):

        # TODO; ili u wrapperu ili u call-u ispitas self (a ne _oriigin.self) ako je true onda znas sta radis :) pustas ga i ako je None

        self.__local_orm_module = None

        if not self.skip_db:
            # __function_module = inspect.getmodule(funct).__name__
            # __local_orm_module_name = '.'.join(__function_module.split('.')[:-1]) + '.orm'

            # __local_orm_module_name = 'orm.orm'
            # a = 'orm.orm'

            try:
                self.__local_orm_module = importlib.import_module('orm.orm')
            except:
                pass

        @wraps(funct)
        async def wrapper(_origin_self, *args, **kwargs):

            try:

                _origin_self.set_header("Access-Control-Allow-Origin", "*")
                _origin_self.set_header("Access-Control-Allow-Headers",
                                        "Origin, X-Requested-With, Content-Type, Accept")
                _origin_self.set_header('Access-Control-Allow-Methods', 'POST, GET, PUT, DELETE, PATCH OPTIONS')

                sig = signature(funct)

                kwa = {}

                from inspect import isclass

                _origin_self.orm_session = None

                if self.__local_orm_module:
                    _origin_self.orm_session = self.__local_orm_module.session()

                if str(sig) != '(self)':

                    if _origin_self.request.body:
                        body = json.loads(_origin_self.request.body.decode('utf-8'))
                    else:
                        body = {}

                    _origin_self.body = body

                    # handler_args = _origin_self.get_arguments()

                    arg_pos = -1
                    for p in sig.parameters:
                        if p == 'self':
                            continue

                        pp = sig.parameters[p]

                        # ispitivanje da li je klasa inspect._empty   !!! uraditi to pametnije !!!

                        passed = False

                        arg_pos += 1

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

                            # TODO: izbaciti kao izuzetak a ne ovako !

                            if pp.annotation == str and not type(value) == str:
                                raise http.General4xx(f"Invalid datatype, int type is expected for {pp.name}")

                                # _origin_self.write(
                                #     json.dumps({"message": f"Invalid datatype, str type is expected for {pp.name}"}))
                                # _origin_self.set_status(http.code.HTTPStatus.BAD_REQUEST)
                                # return

                            elif pp.annotation == int and not type(value) == int:
                                try:
                                    if '.' in value:
                                        raise http.General4xx(f"Invalid datatype, int type is expected for {pp.name}")

                                    value = int(value)
                                except:
                                    raise http.General4xx(f"Invalid datatype, int type is expected for {pp.name}")


                            elif pp.annotation == float and not type(value) in (float, int):
                                try:
                                    value = float(value)
                                except:
                                    raise http.General4xx(f"Invalid datatype, float type is expected for {pp.name}")

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

                            # slucaj kada je paramar sama kalsa, koja se konstrujise iz json-a
                            elif issubclass(pp.annotation, sql_base):
                                model_class = pp.annotation

                                # print("#-"*10)
                                # print("V", value)
                                # print("AUTH", hasattr(_origin_self,'id_user'))
                                #
                                # print("MC", )

                                # ukoliko id_user postoji u modelu, i ukoliko se radi u auth useru, znaci
                                # da je user ulogovan, ako neko pokusava da upise id_usera, radi se o upravo ulogovanom
                                # korisniku, ovo nije dobro jer se time id_user, rezervise za ovu akciju, sto moze
                                # da zezne nekog ko to nema u vidu, takod a treba smisliti nesto bolje

                                if hasattr(model_class, 'id_user') and hasattr(_origin_self, 'id_user'):
                                    value['id_user'] = _origin_self.id_user

                                try:
                                    kwa[pp.name] = model_class(**value)
                                except Exception as e:
                                    _origin_self.write(
                                        json.dumps(
                                            {"message": f"Invalid datatype {pp.annotation} error builiding object"}))
                                    _origin_self.set_status(http.code.HTTPStatus.BAD_REQUEST)

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
                                            {"message": f"Mandatory argument {pp.name} missing in input request"}))
                                    _origin_self.set_status(http.code.HTTPStatus.BAD_REQUEST)
                                    return

                                kwa[pp.name] = value
                            else:

                                if passed:
                                    kwa[pp.name] = value
                                else:
                                    kwa[pp.name] = pp.default

                    # print("KWA",kwa)

                _args = []

                res = await funct(_origin_self, *_args, **kwa)

                if _origin_self.orm_session:
                    print('closing session')
                    _origin_self.orm_session.close()

                status_code = http.code.HTTPStatus.OK

                response = None

                if type(res) == tuple:
                    response = res[0]
                    status_code = res[1]

                if type(res) in (dict, list):
                    response = res

                if isinstance(res, type(None)):
                    response = None
                    status_code = http.code.HTTPStatus.NO_CONTENT

                _origin_self.set_status(status_code)

                if response is not None:
                    _origin_self.write(json.dumps(response))


            except http.HttpErrorUnauthorized as e:
                _origin_self.set_status(e.status)
            except http.General4xx as e:
                _origin_self.set_status(e.status)
            except http.HttpInvalidParam as e:
                self.write(json.dumps({"message": e.message}))
                _origin_self.set_status(e.status)

            except Exception as e:
                # print("-" * 100)
                # import traceback
                # print(e)
                # print("-" * 100)
                _origin_self.write(json.dumps({"message": str(e)}))
                _origin_self.set_status(http.code.HTTPStatus.INTERNAL_SERVER_ERROR)

        return wrapper


class auth:
    def __init__(self, *args, **kwargs):
        pass

    def __call__(self, funct):
        @wraps(funct)
        async def wrapper(_self_origin, *args, **kwargs):

            # _args = []

            # ISTI PROBLEM KAO DOLE
            #
            # if 'Authorization' not in _self_origin.request.headers:
            #     raise http.HttpErrorUnauthorized

            if 'Authorization' in _self_origin.request.headers:

                res, id_user, id_session = token.token2user(_self_origin.request.headers['Authorization'])

                # ?!? iz nekog razloga je prestalo da sljaka
                #
                # ERROR : Exception after Future was cancelled

                # if not res:
                #     raise http.HttpErrorUnauthorized

                if res:
                    _self_origin.id_user = id_user
                    _self_origin.id_session = id_session
                    await funct(_self_origin, *args, **kwargs)
                    return

            _self_origin.set_status(http.code.HTTPStatus.UNAUTHORIZED)
            _self_origin.write('{"message":"unauthorized"}')

        return wrapper


class route:
    uri = []

    @staticmethod
    def register_handler(uri, handler):

        # TODO: handler moze da bude string ili niz stringova

        if not hasattr(route, '_handlers'):
            route._handlers = []

        if not hasattr(route, '_handler_names'):
            route._handler_names = set()

        for _uri, _ in route._handlers:
            if _uri == uri:
                raise NameError(f"Error creating api, endopoint '{_uri}'  already exists")

        route._handlers.append((uri, handler))

    @staticmethod
    def handlers():
        if hasattr(route, '_handlers'):
            return route._handlers

        return []

    @staticmethod
    def handler_names():
        if hasattr(route, '_handler_names'):
            return route._handler_names

        return set()

    @staticmethod
    def set_handler_names(hn):
        route._handler_names = hn

    def __init__(self, *args, **kwargs):

        self.uri = []

        if 'URI' not in kwargs:
            import inspect
            caller_frame = inspect.stack()[1]
            raise NameError("Missing URI in API class from module {}".format(caller_frame[1]))

        # self.uri_args = []

        if type(kwargs['URI']) == str:
            uris = [kwargs['URI']]
        else:
            uris = kwargs['URI']

        for uri in uris:
            parts = uri.split('/')
            rparts = []
            for p in parts:
                rparts.append("(.*)" if len(p) and p[0] == ':' else p)
                # if len(p) and p[0] == ':':
                #     self.uri_args.append(p[1:])

            self.uri.append('/'.join(rparts))

        # print(self.uri, self.uri_args)

    def __call__(self, cls):

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

        from base import registry
        prefix = registry.prefix()

        for uri in self.uri:
            furi = prefix + ('/' if len(uri) > 0 and uri[0] != '/' else '') + uri
            print("URI:", furi)
            route.register_handler(furi, cls)
        return cls


def log_function(handler: tornado.web.RequestHandler):
    logger = getattr(handler, 'logger',
                     logging.getLogger('root'))
    if handler.get_status() < 400:
        level = logging.INFO
    elif handler.get_status() < 500:
        level = logging.WARNING
    else:
        level = logging.ERROR

    logutils.log(
        logger,
        level,
        include_context=True,
        message='RESPONSE',
        status=handler.get_status(),
        time_ms=(1000.0 * handler.request.request_time())
    )
    logutils.clear_log_context()


def make_app():
    full_path = os.path.realpath(__file__)
    my_dir_name = os.path.dirname(full_path)

    try:
        with open(my_dir_name + '/config/logs.yaml') as file:
            log_config = yaml.load(file, Loader=yaml.SafeLoader)
            logging.config.dictConfig(log_config['logging'])
            logger = logging.getLogger(LOGGER_NAME)
            loop = asyncio.get_event_loop()
            loop.set_task_factory(context.task_factory)

    except Exception as e:
        sys.exit()

    return tornado.web.Application(route.handlers(),
                                   debug=True,  # TODO: debug= iz yaml.deebug
                                   log_function=log_function)


def run(port):
    app = make_app()
    app.listen(port)
    tornado.ioloop.IOLoop.current().start()
