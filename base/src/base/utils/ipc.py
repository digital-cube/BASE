import json

from tornado.httpclient import AsyncHTTPClient
import base
from base import http


async def call(request, service, method, endpoint, body=None):
    method = method.upper()

    if base.config.conf['apptype']=='micro-service':
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
        uri = 'http://' + scfg['host'] + prefix + ('/' if endpoint[0]!='/' else '') + endpoint

    else:

        prefix = base.config.conf['services'][service]['prefix']
        host = base.config.conf['host']

        if not base.registry.test:
            port = base.config.conf['port']
        else:
            port = base.registry.test_port

        uri = 'http://' + host + ':' + str(port) + prefix + ('/' if endpoint[0]!='/' else '') + endpoint

    http_client = AsyncHTTPClient()
    headers = {}

    if request and request.headers and base.config.conf['authorization']['key'] in request.headers:
        headers[base.config.conf['authorization']['key']] = request.headers[base.config.conf['authorization']['key']]

    _body = None if method in ('GET', 'DELETE') else json.dumps(body if body else {}, ensure_ascii=False)

    # print("URI", uri)

    try:
        result = await http_client.fetch(uri, method=method, headers=headers, body=_body)
    except Exception as e:
        try:
            resp_body = json.loads(e.response.body)
            message, id_message, code = resp_body['message'], resp_body['id'], resp_body['code']
        except:
            raise http.HttpInternalServerError

        raise http.BaseHttpException(message=message,
                                     id_message=id_message,
                                     status=code)


    return json.loads(result.body.decode('utf-8'))
