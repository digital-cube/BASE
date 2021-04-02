from tornado.testing import AsyncHTTPTestCase
from tornado.ioloop import IOLoop
import json

from uuid import uuid4 as UUIDUUID4

import base64
from base import http


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
            if self.raw_response:
                print('binary content, size=',len(self.r))
            else:
                print(json.dumps(self.r, indent=4, ensure_ascii=False))

    def api(self, token, method, url, body=None,
            expected_code=(http.status.OK, http.status.CREATED, http.status.NO_CONTENT),
            expected_result=None, expected_result_subset=None,
            expected_result_contain_keys=None, expected_length=None, expected_lenght_for_key: tuple = None,
            raw_response=False, headers: dict = {}):

        url = url.strip()
        self.last_uri = url
        self.raw_response = raw_response

        if not body:
            if method in ('PUT', 'POST', 'PATCH'):
                body = {}

        if method in ('GET', 'DELETE'):
            body = None

        from base import config
        if token:
            headers.update({config.conf['authorization']['key']: token})

        import time
        stime = time.time()
        self.execution_time = 'n/a'
        try:
            response = self.fetch(url, method=method,
                                  body=json.dumps(body, ensure_ascii=False) if body is not None else None,
                                  headers=headers)
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
                self.assertEqual(expected_code, response.code)

        if raw_response:
            self.execution_time = time.time() - stime
            self.last_result = response.body
            self.r = response.body
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
            self.assertEqual(res, expected_result)

        if expected_result_contain_keys:
            for key in expected_result_contain_keys:
                self.assertTrue(key in res)

        if expected_result_subset:
            for key in expected_result_subset:
                self.assertTrue(key in res)
                self.assertEqual(res[key], expected_result_subset[key])

        if expected_length is not None:
            self.assertEqual(len(res), expected_length)

        if expected_lenght_for_key is not None:
            self.assertTrue(len(res[expected_lenght_for_key[0]]) == expected_lenght_for_key[1])

        self.r = res
        self.last_result = res
        self.execution_time = time.time() - stime

        return res
