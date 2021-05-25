import json

from tornado.httpclient import AsyncHTTPClient
import base
from base import http
import logging
import os

AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")


async def raw_call(method, full_url_endpoint, body, headers={}, auth_mode=None, username=None, password=None):
    request_timeout = 300

    _body = None if method in ('GET', 'DELETE') else json.dumps(body if body else {}, ensure_ascii=False)

    http_client = AsyncHTTPClient()
    try:
        args = [full_url_endpoint]
        kwargs = {
            'method': method,
            'headers': headers,
            'body': _body,
            'request_timeout': request_timeout,
        }

        if auth_mode:
            kwargs['auth_mode'] = auth_mode
        if username and password:
            kwargs['auth_username'] = username
            kwargs['auth_password'] = password

        try:
            result = await http_client.fetch(*args, **kwargs)
            return json.loads(result.body.decode('utf-8')) if result.body else None, result.code
        except Exception as e:
            logging.getLogger('base').log(level=logging.CRITICAL, msg=str(e))
            return False, None

    except Exception as e:
        logging.getLogger('base').log(level=logging.CRITICAL, msg=f"FAILED {method}:{full_url_endpoint}")
        logging.getLogger('base').log(level=logging.CRITICAL, msg=f"FAILED body: {_body}")

        return False, None


async def call(request, service, method, endpoint, body=None):
    request_timeout = 300

    if not 'services' in base.config.conf:
        raise http.HttpInternalServerError(id_message="SERVICES_NOT_FOUND_IN_CONFIG",
                                           message="services not registered in config")

    if not service in base.config.conf['services']:
        raise http.HttpInternalServerError(id_message="SERVICE_NOT_DEFINED",
                                           message=f"{service} service is not defined")

    host = service
    port = base.config.conf['port']

    prefix = base.config.conf['services'][service]['prefix'].strip('/')
    endpoint = endpoint.strip('/')

    if base.config.conf['apptype'] == 'monolith':
        host = 'localhost'

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
                                         request_timeout=request_timeout,
                                         connect_timeout=request_timeout)

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
