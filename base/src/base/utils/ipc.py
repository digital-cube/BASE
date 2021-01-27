import json

from tornado.httpclient import AsyncHTTPClient
import base
from base import http
import logging
import os


async def call(request, service, method, endpoint, body=None, readonly=False):
    method = method.upper()

    if readonly:
        readonly_supported = os.getenv('USE_READ_REPLICA', 'no').strip().lower() in ('yes', 'true', '1')

        if not readonly_supported:
            readonly = False

    if readonly and method != 'GET':
        raise http.HttpInternalServerError(id_message='IPC_READONLY_SUPPORTED_ONLY_FOR_GET_METHOD',
                                           message='Readonly flag for not get metod')

    import base
    if base.registry.test and base.config.conf['apptype'] == 'micro-service':
        return None

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
        result = await http_client.fetch(uri, method=method, headers=headers, body=_body, request_timeout=600)
        logging.getLogger('ipc').log(level=logging.DEBUG, msg=f"OK {method}:{uri}")

    except Exception as e:
        logging.getLogger('ipc').log(level=logging.CRITICAL, msg=f"FAILED {method}:{uri}")
        logging.getLogger('ipc').log(level=logging.CRITICAL, msg=f"FAILED body: {_body}")
        logging.getLogger('ipc').log(level=logging.CRITICAL, msg=f"FAILED response-code: {e.response.code}")
        logging.getLogger('ipc').log(level=logging.CRITICAL, msg=f"FAILED response-body: {e.response.body}")
        print(f"\nIPC FAILED, {e}\n")

        resp_body = None
        try:
            resp_body = json.loads(e.response.body)
            message, id_message, code = resp_body['message'], resp_body['id'], resp_body['code']
        except:
            raise http.HttpInternalServerError(id_message=str(resp_body))

        raise http.BaseHttpException(message=message,
                                     id_message=id_message,
                                     status=code)

    return json.loads(result.body.decode('utf-8'))
