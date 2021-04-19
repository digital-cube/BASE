from tornado.testing import AsyncHTTPTestCase
from tornado.ioloop import IOLoop
import json
from base import http

from uuid import uuid4 as UUIDUUID4

import base64


class MockedRedis:
    store = {}

    def set(self, key, value):
        value = value.encode()
        MockedRedis.store[key] = value

    def get(self, key):
        return MockedRedis.store[key]

    def flushall(self):
        MockedRedis.store = {}


def b64file(fn):
    with open(fn, 'rb') as f:
        content = f.read()
    res = base64.encodebytes(content)
    return res.decode('utf-8')


def my_uuid4():
    if not hasattr(my_uuid4, 'next'):
        my_uuid4.next = 0
        my_uuid4.history = []

    res = UUIDUUID4()

    # res = uuid.UUID(f'00000000-0000-0000-0000-{my_uuid4.next:012d}')
    my_uuid4.history.append(str(res))
    my_uuid4.next += 1
    return res


class BaseTest(AsyncHTTPTestCase):

    def setUp(self):
        super(BaseTest, self).setUp()
        self.r = None
        self.last_result = None
        pass

    def get_new_ioloop(self):
        return IOLoop.current()

    def get_app(self):
        return self.my_app

    def show_last_result(self, marker='LAST_RES'):
        if hasattr(self, 'last_uri'):
            print(f"{marker} :: URI", self.last_uri)
        if hasattr(self, 'code'):
            print(f"{marker} :: code =", self.code, "EXECUTE TIME", self.execution_time)
        if hasattr(self, 'r'):
            print(f"{marker} :: Last result content")
            print(json.dumps(self.r, indent=4, ensure_ascii=False))

    def api(self, token, method, url, body=None,
            expected_code=(http.status.OK, http.status.CREATED, http.status.NO_CONTENT), expected_result=None, expected_result_subset=None,
            expected_result_contain_keys=None, expected_length=None,expected_lenght_for_key: tuple = None,
            raw_response=False, headers={}, default_timeout=600):

        url = url.strip()
        self.last_uri = url

        if not body:
            if method in ('PUT', 'POST', 'PATCH'):
                body = {}

        if method in ('GET', 'DELETE'):
            body = None
        else:
            body = json.dumps(body)

        from base import config
        # headers = {config.conf['authorization']['key']: token} if token else {}

        # TODO: Check out this !!!
        headers.update({config.conf['authorization']['key']: token} if token else {})

        import time
        stime = time.time()
        self.execution_time = 'n/a'
        try:
            self.http_client.configure(None, 
            #connect_timeout=default_timeout, 
            #request_timeout=default_timeout
            )

            response = self.fetch(url, method=method,
                                  body=body,
                                  headers=headers,
#                                  connect_timeout=default_timeout,
                                  request_timeout=default_timeout)
        except Exception as e:
            print('error serializing output ', e, e)
            print("body", type(body), body)
            print('_' * 100)
            print("")
            self.assertTrue(False)

        self.code = response.code
        if expected_code:
            if type(expected_code) == tuple:
                self.assertIn(response.code, expected_code)
            else:
                self.assertEqual(expected_code, response.code, msg=response.body)

        if raw_response:
            self.execution_time = time.time() - stime
            return response.body

        resp_txt = response.body.decode('utf-8')

        try:
            res = json.loads(resp_txt) if resp_txt else {}
            self.r = res
            self.last_result = res
        except:
            print("Error decoding following response")
            print(resp_txt)
            print("-" * 100)
            self.assertTrue(False)

        if expected_result:
            self.assertEqual(expected_result, res)

        if expected_result_contain_keys:
            for key in expected_result_contain_keys:
                self.assertTrue(key in res)

        if expected_result_subset:
            for key in expected_result_subset:
                self.assertTrue(key in res)
                self.assertEqual(expected_result_subset[key], res[key])

        if expected_length is not None:
            self.assertEqual(expected_length, len(res))

        if expected_lenght_for_key is not None:
            self.assertTrue(len(res[expected_lenght_for_key[0]]) == expected_lenght_for_key[1])


        self.r = res
        self.last_result = res
        self.execution_time = time.time() - stime

        return res
