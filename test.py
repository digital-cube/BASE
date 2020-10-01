from tornado.testing import AsyncHTTPTestCase
from tornado.ioloop import IOLoop
import json

from uuid import uuid4 as UUIDUUID4

def b64file(fn):
    import base64
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
        pass

    def get_new_ioloop(self):
        return IOLoop.current()

    def get_app(self):
        return self.my_app

    def api(self, token, method, url, body=None,
            expected_code=None, expected_result=None, expected_result_subset=None,
            expected_result_contain_keys=None,
            raw_response=False):

        url = url.strip()

        if not body:
            if method in ('PUT', 'POST', 'PATCH'):
                body = {}

        headers = {"Authorization": token} if token else {}

        response = self.fetch(url, method=method, body=json.dumps(body) if body is not None else None, headers=headers)


        if expected_code:
            self.assertEqual(expected_code, response.code)

        if raw_response:
            return response.body

        resp_txt = response.body.decode('utf-8')

        # print("RESP_TXT",resp_txt)

        try:
            res = json.loads(resp_txt) if resp_txt else {}
        except:
            print("Error decoding following response")
            print(resp_txt)
            print("-"*100)
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

        return res
