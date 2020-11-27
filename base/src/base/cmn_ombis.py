import json
from base import config, http

from tornado.httpclient import AsyncHTTPClient

AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")


async def get(url):
    try:
        ocfg = config.conf['ombis']
        host = ocfg['host']
        port = ocfg['port']
        user = ocfg['user']
        password = ocfg['password']
    except:
        ocfg = None

    if not ocfg:
        raise http.HttpInternalServerError(id_message='INVALID_CONFIGURATION',
                                           message='Ombis not proprely configured')

    client = AsyncHTTPClient()

    url = f'http://{host}:{port}{url}'
    print('URL',url)
    res = await client.fetch(url, auth_username=user, auth_password=password, auth_mode='digest')

    data = json.loads(res.body.decode('utf-8'))
    return data

