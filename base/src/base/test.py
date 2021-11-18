from tornado.testing import AsyncHTTPTestCase
from tornado.ioloop import IOLoop
import json
from base import http

from uuid import uuid4 as UUIDUUID4

import base64
import uuid


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


def is_uuid(s):
    if type(s) == uuid.UUID:
        return True
    try:
        uuid.UUID(s)
    except:
        return False
    return True


def clear_uuid_values_in_list(lst):
    pos = -1
    for item in lst:
        pos += 1
        if type(item) == dict:
            clear_uuid_values(lst[pos])
            continue
        if type(item) == list:
            clear_uuid_values_in_list(lst[pos])
            continue
        if is_uuid(item):
            lst[pos] = '__IGNORE_THIS_UUID__'


def clear_uuid_values(dct):
    if type(dct) == list:
        clear_uuid_values_in_list(dct)
        return

    for key in dct:
        val = dct[key]

        if type(val) == list:
            clear_uuid_values_in_list(val)
            continue


        elif type(val) == dict:
            clear_uuid_values(val)
            continue

        if is_uuid(val):
            dct[key] = '__IGNORE_THIS_UUID__'


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
            expected_result_contain_keys=None, expected_length=None, expected_lenght_for_key: tuple = None,
            raw_response=False, headers=None, default_timeout=600,
            ignore_uuid_values=False,
            ):

        if not headers:
            headers = {}

        url = url.strip()
        self.last_uri = url

        if not body:
            if method in ('PUT', 'POST', 'PATCH'):
                body = {}

        if method in ('GET', 'DELETE'):
            body = None
        else:
            try:
                body = json.dumps(body)
            except Exception as e:
                raise

        from base import config
        # headers = {config.conf['authorization']['key']: token} if token else {}

        # TODO: Check out this !!!
        headers.update({config.conf['authorization']['key']: token} if token else {})

        import time
        stime = time.time()
        self.execution_time = 'n/a'
        try:
            self.http_client.configure(None,
                                       # connect_timeout=default_timeout,
                                       # request_timeout=default_timeout
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

        import copy

        res4ret = copy.deepcopy(res)
        if ignore_uuid_values:
            clear_uuid_values(res)
            if expected_result:
                expected_result = clear_uuid_values(expected_result)
            if expected_result_subset:
                expected_result_subset = clear_uuid_values(expected_result_subset)

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

        self.r = res4ret
        self.last_result = res4ret
        self.execution_time = time.time() - stime

        return res
