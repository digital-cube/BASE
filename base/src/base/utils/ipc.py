import json

from tornado.httpclient import AsyncHTTPClient
import base
from base import http
import logging
import os


async def call_raw(request, method, fullurl, body=None, exected_format='json', headers={}, username=None, password=None):
    request_timeout = 300

    if request and request.headers and base.config.conf['authorization']['key'] in request.headers:
        if base.config.conf['authorization']['key'] not in headers:
            headers[base.config.conf['authorization']['key']] = request.headers[
                base.config.conf['authorization']['key']]

    _body = None if method in ('GET', 'DELETE') else json.dumps(body if body else {}, ensure_ascii=False)

    http_client = AsyncHTTPClient()
    try:
        result = await http_client.fetch(fullurl,
                                         method=method,
                                         headers=headers,
                                         body=_body,
                                         request_timeout=request_timeout,
                                         auth_username=username,
                                         auth_password=password
                                         )

        try:
            if exected_format == 'json':
                return json.loads(result.body.decode('utf-8')) if result.body else None, result.code
            else:
                return result.body, result.code

        except Exception as e:
            logging.getLogger('base').log(level=logging.CRITICAL, msg=str(e))

    except Exception as e:
        try:
            logging.getLogger('base').log(level=logging.CRITICAL, msg=f"FAILED {method}:{method}")
            logging.getLogger('base').log(level=logging.CRITICAL, msg=f"body {_body}")
        except Exception as e:
            logging.getLogger('base').log(level=logging.CRITICAL, msg=str(e))


async def call_new(request, service, method, endpoint, body=None):
    request_timeout = 300

    if not 'services' in base.config.conf:
        raise http.HttpInternalServerError(id_message="SERVICES_NOT_FOUND_IN_CONFIG",
                                           message="services not registered in config")

    if not service in base.config.conf['services']:
        raise http.HttpInternalServerError(id_message="SERVICE_NOT_DEFINED",
                                           message=f"{service} service is not defined")

    host = base.config.conf['host']
    port = base.config.conf['port']

    prefix = base.config.conf['services'][service]['prefix'].strip('/')
    endpoint = endpoint.strip('/')

    if base.registry.test:
        request_timeout = 3600
        host = 'localhost'
        port = base.registry.test_port

    uri = f'http://{host}:{port}/{prefix}/{endpoint}'

    headers = {}

    if request and request.headers and base.config.conf['authorization']['key'] in request.headers:
        headers[base.config.conf['authorization']['key']] = request.headers[base.config.conf['authorization']['key']]

    _body = None if method in ('GET', 'DELETE') else json.dumps(body if body else {}, ensure_ascii=False)

    http_client = AsyncHTTPClient()
    try:
        result = await http_client.fetch(uri,
                                         method=method,
                                         headers=headers,
                                         body=_body,
                                         request_timeout=request_timeout)

        try:
            return json.loads(result.body.decode('utf-8')) if result.body else None, result.code
        except Exception as e:
            logging.getLogger('base').log(level=logging.CRITICAL, msg=str(e))

    except Exception as e:
        try:
            logging.getLogger('base').log(level=logging.CRITICAL, msg=f"FAILED {method}:{uri}")
            logging.getLogger('base').log(level=logging.CRITICAL, msg=f"FAILED body: {_body}")
            logging.getLogger('base').log(level=logging.CRITICAL, msg=f"FAILED response-code: {e.response.code}")
            logging.getLogger('base').log(level=logging.CRITICAL, msg=f"FAILED response-body: {e.response.body}")
        except Exception as e:
            logging.getLogger('base').log(level=logging.CRITICAL, msg=f"FAILED {e}")


def lprint(s):
    import os
    from base import config as bconfig

    svcname = bconfig.conf["name"]

    __pfx = '/logs/' if os.getenv('ENVIRONMENT', 'local') == 'docker' else '/tmp/'

    with open(__pfx + 'trace.log', 'at') as f:
        f.write(f'{s}\n'.replace("__svcname__", f'{svcname[:10]:>10} '))

    with open(__pfx + f'trace.{svcname}.log', 'at') as f:
        f.write(f'{s}\n')


async def call(request, service, method, endpoint, body=None, readonly=False):
    method = method.upper()

    from base.src.base.app import __indent__
    import datetime
    indent = __indent__ * '.'
    import uuid
    __id = f'ipc {str(uuid.uuid4())[:4]}'
    from base import config
    fname = f'{config.conf["name"]} calling {service}'

    lprint(f"{str(datetime.datetime.now()):>30} {' ':>10} __svcname__ in    : {__id} {indent} > {fname}")

    if readonly:
        readonly_supported = os.getenv('USE_READ_REPLICA', 'no').strip().lower() in ('yes', 'true', '1')

        if not readonly_supported:
            readonly = False

    if readonly and method != 'GET':
        raise http.HttpInternalServerError(id_message='IPC_READONLY_SUPPORTED_ONLY_FOR_GET_METHOD',
                                           message='Readonly flag for not get metod')

    import base
    # if base.registry.test and base.config.conf['apptype'] == 'micro-service':
    #     return None

    if base.config.conf['apptype'] == 'micro-service':
        if not base.store.exists('services'):
            raise http.HttpInternalServerError(id_message="INTERNAL_SERVER_ERROR",
                                               message="services not registered in store")

        services = json.loads(base.store.get('services'))
        if service not in services:
            raise http.HttpInternalServerError(id_message="INTERNAL_SERVER_ERROR",
                                               message=f"service {service} not registered in store.services")

        scfg = base.store.get(f'base_svc_{service}')
        if not scfg:
            raise http.HttpInternalServerError(id_message="INTERNAL_SERVER_ERROR",
                                               message=f"configuration for service {service} not registered in store")

        scfg = json.loads(scfg)
        if 'prefix' not in scfg:
            raise http.HttpInternalServerError(id_message="INTERNAL_SERVER_ERROR",
                                               message=f"missing prefix in service configuration")
        prefix = scfg['prefix']

        port = base.registry.test_port if base.registry.test else scfg['port']

        ro = '_read' if readonly else ''

        uri = 'http://' + scfg['host'] + ro + ':' + str(port) + prefix + ('/' if endpoint[0] != '/' else '') + endpoint

    else:

        prefix = base.config.conf['services'][service]['prefix']
        host = base.config.conf['host']

        if not base.registry.test:
            port = base.config.conf['port']
        else:
            port = base.registry.test_port

        uri = 'http://' + host + ':' + str(port) + prefix + ('/' if endpoint[0] != '/' else '') + endpoint

    # print("-"*100)
    # print(uri)

    http_client = AsyncHTTPClient()
    headers = {}

    if request and request.headers and base.config.conf['authorization']['key'] in request.headers:
        headers[base.config.conf['authorization']['key']] = request.headers[base.config.conf['authorization']['key']]

    _body = None if method in ('GET', 'DELETE') else json.dumps(body if body else {}, ensure_ascii=False)

    logging.getLogger('ipc').log(level=logging.DEBUG, msg=f"{method}:{uri}")
    try:
        # if 'unique_id' in uri:
        #     print('stop')
        # print('-'*100)
        # print("URI",method,uri)

        result = await http_client.fetch(uri, method=method, headers=headers, body=_body, request_timeout=600)

        lprint(f"{str(datetime.datetime.now()):>30} {' ':>10} __svcname__ out   : {__id} {indent} < {fname} (OK) {'/'.join(uri.split('/')[3:]).split('?')[0]}")

        logging.getLogger('ipc').log(level=logging.DEBUG, msg=f"OK {method}:{uri}")

    except Exception as e:

        lprint(f"{str(datetime.datetime.now()):>30} {' ':>10} __svcname__ out   : {__id} {indent} < {fname} (ERR) {e}")

        print('EXCEPT IPC', uri)
        logging.getLogger('ipc').log(level=logging.CRITICAL, msg=f"FAILED {method}:{uri}")
        # logging.getLogger('ipc').log(level=logging.CRITICAL, msg=f"FAILED body: {_body}")
        try:
            logging.getLogger('ipc').log(level=logging.CRITICAL, msg=f"FAILED response-code: {e.response.code}")
        except:
            logging.getLogger('ipc').log(level=logging.CRITICAL, msg='cannt log e.response.code')
            pass
            
        try:
            logging.getLogger('ipc').log(level=logging.CRITICAL, msg=f"FAILED response-body: {e.response.body}")
        except:
            logging.getLogger('ipc').log(level=logging.CRITICAL, msg='cannt log e.response.body')
            pass
            
        print(f"\nIPC FAILED, {e}\n")

        resp_body = None
        try:
            resp_body = json.loads(e.response.body)

            # print("----- EXCEPTION -----"+'-'*100)
            # print(resp_body)
            # print("----- /EXCEPTION -----"+'-'*100)

            message = resp_body['message'] if 'message' in resp_body else 'unknown message'
            id_message = resp_body['id'] if 'id' in resp_body else 'unknown id message'
            code = resp_body['code'] if 'code' in resp_body else 400
            # message, id_message, code = resp_body['message'], resp_body['id'], resp_body['code']
        except:
            raise http.HttpInternalServerError(id_message=str(resp_body))

        raise http.BaseHttpException(message=message,
                                     id_message=id_message,
                                     status=code)

    return json.loads(result.body.decode('utf-8')) if result.body else None
