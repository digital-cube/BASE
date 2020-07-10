# coding: utf-8

import json
from decimal import Decimal
from tornado.httputil import url_concat
from base.tests.helpers.testing import TestBase
from base.application.lookup import responses


class TestHello(TestBase):

    def test_get_unauthorized(self):

        res = self.fetch('/api/hello')

        self.assertEqual(res.code, 200)
        res = res.body.decode('utf-8')
        res = json.loads(res)

        self.assertIn('d_bool', res)
        self.assertIn('d_int', res)
        self.assertIn('d_float', res)
        self.assertIn('d_list', res)
        self.assertIn('d_dict', res)
        self.assertIn('d_dec', res)
        self.assertIn('d_json', res)
        self.assertIn('d_email', res)
        self.assertIn('d_datetime', res)
        self.assertIn('d_date', res)
        self.assertIn('d_seq', res)

    def test_get(self):

        _params = {
            'd_bool': False,
            'd_int': 20,
            'd_float': 20.01,
            'd_list': [1, 2, 3, 4],
            'd_dict': json.dumps({'1': 1, '2': 2, '3': 3, '4': 4}),
            'd_dec': 25.10,
            'd_json': json.dumps({'5': 5, '6': 6, '7': 7, '8': 8}),
            'd_email': 'test@test.loc',
            'd_datetime': '2017-03-03 22:15:15',
            'd_date': '2017-03-03'
        }
        _url = url_concat('/api/hello', _params)
        res = self.fetch(_url)

        self.assertEqual(res.code, 200)
        res = res.body.decode('utf-8')
        res = json.loads(res)

        self.assertIn('d_bool', res)
        self.assertEqual(res['d_bool'], False)
        self.assertIn('d_int', res)
        self.assertEqual(res['d_int'], 20)
        self.assertIn('d_float', res)
        self.assertEqual(res['d_float'], 20.01)
        self.assertIn('d_list', res)
        self.assertEqual(res['d_list'], [1, 2, 3, 4])
        self.assertIn('d_dict', res)
        self.assertEqual(res['d_dict'], {'1': 1, '2': 2, '3': 3, '4': 4})
        self.assertIn('d_dec', res)
        self.assertEqual(res['d_dec'], '25.1')
        self.assertIn('d_json', res)
        self.assertEqual(res['d_json'], {'5': 5, '6': 6, '7': 7, '8': 8})
        self.assertIn('d_email', res)
        self.assertEqual(res['d_email'], 'test@test.loc')
        self.assertIn('d_datetime', res)
        self.assertEqual(res['d_datetime'], '2017-03-03 22:15:15')
        self.assertIn('d_date', res)
        self.assertEqual(res['d_date'], '2017-03-03')
        self.assertIn('d_seq', res)
        self.assertEqual(res['d_seq'], None)

    def test_get_with_different_params_types(self):

        _params = {
            'd_bool': 'test bool',
            'd_int': '20',
            'd_float': '20.8',
            'd_list': '[1, 2, 3, 4]',
            'd_dict': json.dumps({'1': '1', '2': '2', '3': '3', '4': '4'}),
            'd_dec': '25.10',
            'd_json': json.dumps([5, 6, 7, 8]),
            'd_email': 'test@test',
            'd_datetime': '2017-03-08 02:15:15',
            'd_date': '2017-03-08',
        }
        _url = url_concat('/api/hello', _params)
        res = self.fetch(_url)

        self.assertEqual(res.code, 200)
        res = res.body.decode('utf-8')
        res = json.loads(res)

        self.assertIn('d_bool', res)
        self.assertEqual(res['d_bool'], False)
        self.assertIn('d_int', res)
        self.assertEqual(res['d_int'], 20)
        self.assertIn('d_float', res)
        self.assertEqual(res['d_float'], 20.8)
        self.assertIn('d_list', res)
        self.assertEqual(res['d_list'], [1, 2, 3, 4])
        self.assertIn('d_dict', res)
        self.assertEqual(res['d_dict'], {'1': '1', '2': '2', '3': '3', '4': '4'})
        self.assertIn('d_dec', res)
        self.assertEqual(res['d_dec'], '25.10')
        self.assertIn('d_json', res)
        self.assertEqual(res['d_json'], [5, 6, 7, 8])
        self.assertIn('d_email', res)
        self.assertEqual(res['d_email'], 'test@test')
        self.assertIn('d_datetime', res)
        self.assertEqual(res['d_datetime'], '2017-03-08 02:15:15')
        self.assertIn('d_date', res)
        self.assertEqual(res['d_date'], '2017-03-08')
        self.assertIn('d_seq', res)
        self.assertEqual(res['d_seq'], None)

    def test_get_with_wrong_list_type(self):

        _params = {
            'd_bool': False,
            'd_int': 20,
            'd_float': 20.01,
            'd_list': 21,
            'd_dict': json.dumps({'1': 1, '2': 2, '3': 3, '4': 4}),
            'd_dec': 25.10,
            'd_json': json.dumps({'5': 5, '6': 6, '7': 7, '8': 8}),
            'd_email': 'test@test.loc',
            'd_datetime': '2017-03-03 22:15:15',
            'd_date': '2017-03-03',
        }
        _url = url_concat('/api/hello', _params)
        res = self.fetch(_url)

        self.assertEqual(res.code, 400)
        res = res.body.decode('utf-8')
        res = json.loads(res)

        self.assertIn('message', res)
        self.assertEqual(res['message'], responses.lmap[responses.INVALID_REQUEST_ARGUMENT])

    def test_get_with_wrong_date_type(self):

        _params = {
            'd_bool': False,
            'd_int': 20,
            'd_float': 20.01,
            'd_list': [1, 2, 3, 4],
            'd_dict': json.dumps({'1': 1, '2': 2, '3': 3, '4': 4}),
            'd_dec': 25.10,
            'd_json': json.dumps({'5': 5, '6': 6, '7': 7, '8': 8}),
            'd_email': 'test@test.loc',
            'd_datetime': '2017-03-03 22:15:15',
            'd_date': '2017-13-33',
        }
        _url = url_concat('/api/hello', _params)
        res = self.fetch(_url)

        self.assertEqual(res.code, 400)
        res = res.body.decode('utf-8')
        res = json.loads(res)

        self.assertIn('message', res)
        self.assertEqual(res['message'], responses.lmap[responses.INVALID_REQUEST_ARGUMENT])

    def test_get_with_wrong_datetime_type(self):

        _params = {
            'd_bool': False,
            'd_int': 20,
            'd_float': 20.01,
            'd_list': [1, 2, 3, 4],
            'd_dict': json.dumps({'1': 1, '2': 2, '3': 3, '4': 4}),
            'd_dec': 25.10,
            'd_json': json.dumps({'5': 5, '6': 6, '7': 7, '8': 8}),
            'd_email': 'test@test.loc',
            'd_datetime': '2017-13-33 22:15:15',
            'd_date': '2017-03-03',
        }
        _url = url_concat('/api/hello', _params)
        res = self.fetch(_url)

        self.assertEqual(res.code, 400)
        res = res.body.decode('utf-8')
        res = json.loads(res)

        self.assertIn('message', res)
        self.assertEqual(res['message'], responses.lmap[responses.INVALID_REQUEST_ARGUMENT])

    def test_get_with_int_below_the_min(self):

        _params = {
            'd_bool': False,
            'd_int': 9,
            'd_float': 20.01,
            'd_list': [1, 2, 3, 4],
            'd_dict': json.dumps({'1': '1', '2': '2', '3': '3', '4': '4'}),
            'd_dec': 25.10,
            'd_json': json.dumps({'5': 5, '6': 6, '7': 7, '8': 8}),
            'd_email': 'test@test.loc',
            'd_datetime': '2017-03-03 22:15:15',
            'd_date': '2017-03-03',
            'd_seq': 'udummyseqid',
        }
        _url = url_concat('/api/hello', _params)
        res = self.fetch(_url)

        self.assertEqual(res.code, 400)
        res = res.body.decode('utf-8')
        res = json.loads(res)

        self.assertIn('message', res)
        self.assertEqual(res['message'], responses.lmap[responses.ARGUMENT_LOWER_THEN_MINIMUM])

    def test_get_with_float_below_the_min(self):

        _params = {
            'd_bool': False,
            'd_int': 10,
            'd_float': 9.01,
            'd_list': [1, 2, 3, 4],
            'd_dec': 25.10,
            'd_json': json.dumps({'5': 5, '6': 6, '7': 7, '8': 8}),
            'd_email': 'test@test.loc',
            'd_datetime': '2017-03-03 22:15:15',
            'd_date': '2017-03-03',
            'd_seq': 'udummyseqid',
        }
        _url = url_concat('/api/hello', _params)
        res = self.fetch(_url)

        self.assertEqual(res.code, 400)
        res = res.body.decode('utf-8')
        res = json.loads(res)

        self.assertIn('message', res)
        self.assertEqual(res['message'], responses.lmap[responses.ARGUMENT_LOWER_THEN_MINIMUM])

    def test_get_with_list_below_the_minimum(self):

        _params = {
            'd_bool': False,
            'd_int': 20,
            'd_float': 20.01,
            'd_list': [1, 2],
            'd_dict': json.dumps({'1': '1', '2': '2', '3': '3', '4': '4'}),
            'd_dec': 25.10,
        }
        _url = url_concat('/api/hello', _params)
        res = self.fetch(_url)

        self.assertEqual(res.code, 400)
        res = res.body.decode('utf-8')
        res = json.loads(res)

        self.assertIn('message', res)
        self.assertEqual(res['message'], responses.lmap[responses.ARGUMENT_LOWER_THEN_MINIMUM])

    def test_get_with_decimal_below_the_minimum(self):

        _params = {
            'd_bool': False,
            'd_int': 20,
            'd_float': 20.01,
            'd_list': [1, 2, 3, 4],
            'd_dict': json.dumps({'1': 1, '2': 2, '3': 3, '4': 4}),
            'd_dec': 5.10,
            'd_json': json.dumps({'5': 5, '6': 6, '7': 7, '8': 8}),
            'd_email': 'test@test.loc',
            'd_datetime': '2017-03-03 22:15:15',
            'd_date': '2017-03-03',
            'd_seq': 'udummyseqid',
        }
        _url = url_concat('/api/hello', _params)
        res = self.fetch(_url)

        self.assertEqual(res.code, 400)
        res = res.body.decode('utf-8')
        res = json.loads(res)

        self.assertIn('message', res)
        self.assertEqual(res['message'], responses.lmap[responses.ARGUMENT_LOWER_THEN_MINIMUM])

    def test_get_with_datetime_below_the_minimum(self):

        _params = {
            'd_bool': False,
            'd_int': 20,
            'd_float': 20.01,
            'd_list': [1, 2, 3, 4],
            'd_dict': json.dumps({'1': 1, '2': 2, '3': 3, '4': 4}),
            'd_dec': 25.10,
            'd_json': json.dumps({'5': 5, '6': 6, '7': 7, '8': 8}),
            'd_email': 'test@test.loc',
            'd_datetime': '2017-03-02 12:15:15',
            'd_date': '2017-03-03',
            'd_seq': 'udummyseqid',
        }
        _url = url_concat('/api/hello', _params)
        res = self.fetch(_url)

        self.assertEqual(res.code, 400)
        res = res.body.decode('utf-8')
        res = json.loads(res)

        self.assertIn('message', res)
        self.assertEqual(res['message'], responses.lmap[responses.ARGUMENT_LOWER_THEN_MINIMUM])

    def test_get_with_date_below_the_minimum(self):

        _params = {
            'd_bool': False,
            'd_int': 20,
            'd_float': 20.01,
            'd_list': [1, 2, 3, 4],
            'd_dict': json.dumps({'1': 1, '2': 2, '3': 3, '4': 4}),
            'd_dec': 25.10,
            'd_json': json.dumps({'5': 5, '6': 6, '7': 7, '8': 8}),
            'd_email': 'test@test.loc',
            'd_datetime': '2017-03-03 22:15:15',
            'd_date': '2017-03-01',
            'd_seq': 'udummyseqid',
        }
        _url = url_concat('/api/hello', _params)
        res = self.fetch(_url)

        self.assertEqual(res.code, 400)
        res = res.body.decode('utf-8')
        res = json.loads(res)

        self.assertIn('message', res)
        self.assertEqual(res['message'], responses.lmap[responses.ARGUMENT_LOWER_THEN_MINIMUM])

    def test_get_with_int_above_the_max(self):

        _params = {
            'd_bool': False,
            'd_int': 900,
            'd_float': 20.01,
            'd_list': [1, 2, 3, 4],
            'd_dict': json.dumps({'1': '1', '2': '2', '3': '3', '4': '4'}),
            'd_dec': 25.10,
            'd_json': json.dumps({'5': 5, '6': 6, '7': 7, '8': 8}),
            'd_email': 'test@test.loc',
            'd_datetime': '2017-03-03 22:15:15',
            'd_date': '2017-03-03',
            'd_seq': 'udummyseqid',
        }
        _url = url_concat('/api/hello', _params)
        res = self.fetch(_url)

        self.assertEqual(res.code, 400)
        res = res.body.decode('utf-8')
        res = json.loads(res)

        self.assertIn('message', res)
        self.assertEqual(res['message'], responses.lmap[responses.ARGUMENT_HIGHER_THEN_MAXIMUM])

    def test_get_with_float_above_the_max(self):

        _params = {
            'd_bool': False,
            'd_int': 100,
            'd_float': 100.03,
            'd_list': [1, 2, 3, 4],
            'd_dict': json.dumps({'1': '1', '2': '2', '3': '3', '4': '4'}),
            'd_dec': 25.10,
            'd_json': json.dumps({'5': 5, '6': 6, '7': 7, '8': 8}),
            'd_email': 'test@test.loc',
            'd_datetime': '2017-03-03 22:15:15',
            'd_date': '2017-03-03',
            'd_seq': 'udummyseqid',
        }
        _url = url_concat('/api/hello', _params)
        res = self.fetch(_url)

        self.assertEqual(res.code, 400)
        res = res.body.decode('utf-8')
        res = json.loads(res)

        self.assertIn('message', res)
        self.assertEqual(res['message'], responses.lmap[responses.ARGUMENT_HIGHER_THEN_MAXIMUM])

    def test_get_with_list_above_the_max(self):

        _params = {
            'd_bool': False,
            'd_int': 20,
            'd_float': 20.01,
            'd_list': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
            'd_dict': json.dumps({'1': '1', '2': '2', '3': '3', '4': '4'}),
            'd_dec': 25.10,
            'd_json': json.dumps({'5': 5, '6': 6, '7': 7, '8': 8}),
            'd_email': 'test@test.loc',
            'd_datetime': '2017-03-03 22:15:15',
            'd_date': '2017-03-03',
            'd_seq': 'udummyseqid',
        }
        _url = url_concat('/api/hello', _params)
        res = self.fetch(_url)

        self.assertEqual(res.code, 400)
        res = res.body.decode('utf-8')
        res = json.loads(res)

        self.assertIn('message', res)
        self.assertEqual(res['message'], responses.lmap[responses.ARGUMENT_HIGHER_THEN_MAXIMUM])

    def test_get_with_decimal_above_the_max(self):

        _params = {
            'd_bool': False,
            'd_int': 20,
            'd_float': 20.01,
            'd_list': [1, 2, 3, 4],
            'd_dict': json.dumps({'1': 1, '2': 2, '3': 3, '4': 4}),
            'd_dec': 65.10,
            'd_json': json.dumps({'5': 5, '6': 6, '7': 7, '8': 8}),
            'd_email': 'test@test.loc',
            'd_datetime': '2017-03-03 22:15:15',
            'd_date': '2017-03-03',
            'd_seq': 'udummyseqid',
        }
        _url = url_concat('/api/hello', _params)
        res = self.fetch(_url)

        self.assertEqual(res.code, 400)
        res = res.body.decode('utf-8')
        res = json.loads(res)

        self.assertIn('message', res)
        self.assertEqual(res['message'], responses.lmap[responses.ARGUMENT_HIGHER_THEN_MAXIMUM])

    def test_get_with_datetime_above_the_max(self):

        _params = {
            'd_bool': False,
            'd_int': 20,
            'd_float': 20.01,
            'd_list': [1, 2, 3, 4],
            'd_dict': json.dumps({'1': 1, '2': 2, '3': 3, '4': 4}),
            'd_dec': 25.10,
            'd_json': json.dumps({'5': 5, '6': 6, '7': 7, '8': 8}),
            'd_email': 'test@test.loc',
            'd_datetime': '2017-03-12 12:15:15',
            'd_date': '2017-03-03',
            'd_seq': 'udummyseqid',
        }
        _url = url_concat('/api/hello', _params)
        res = self.fetch(_url)

        self.assertEqual(res.code, 400)
        res = res.body.decode('utf-8')
        res = json.loads(res)

        self.assertIn('message', res)
        self.assertEqual(res['message'], responses.lmap[responses.ARGUMENT_HIGHER_THEN_MAXIMUM])

    def test_get_with_date_above_the_minimum(self):

        _params = {
            'd_bool': False,
            'd_int': 20,
            'd_float': 20.01,
            'd_list': [1, 2, 3, 4],
            'd_dict': json.dumps({'1': 1, '2': 2, '3': 3, '4': 4}),
            'd_dec': 25.10,
            'd_json': json.dumps({'5': 5, '6': 6, '7': 7, '8': 8}),
            'd_email': 'test@test.loc',
            'd_datetime': '2017-03-03 22:15:15',
            'd_date': '2017-03-11',
            'd_seq': 'udummyseqid',
        }
        _url = url_concat('/api/hello', _params)
        res = self.fetch(_url)

        self.assertEqual(res.code, 400)
        res = res.body.decode('utf-8')
        res = json.loads(res)

        self.assertIn('message', res)
        self.assertEqual(res['message'], responses.lmap[responses.ARGUMENT_HIGHER_THEN_MAXIMUM])

    def test_put_without_non_required_arguments(self):

        res = self.fetch('/api/hello', method='PUT', body='{}')

        self.assertEqual(res.code, 200)
        res = res.body.decode('utf-8')
        res = json.loads(res)

        self.assertIn('d_bool', res)
        self.assertEqual(res['d_bool'], None)
        self.assertIn('d_int', res)
        self.assertEqual(res['d_int'], None)
        self.assertIn('d_float', res)
        self.assertEqual(res['d_float'], None)
        self.assertIn('d_list', res)
        self.assertEqual(res['d_list'], None)
        self.assertIn('d_dict', res)
        self.assertEqual(res['d_dict'], None)
        self.assertIn('d_dec', res)
        self.assertEqual(res['d_dec'], None)
        self.assertIn('d_json', res)
        self.assertEqual(res['d_json'], None)
        self.assertIn('d_email', res)
        self.assertEqual(res['d_email'], None)
        self.assertIn('d_datetime', res)
        self.assertEqual(res['d_datetime'], None)
        self.assertIn('d_date', res)
        self.assertEqual(res['d_date'], None)
        self.assertIn('d_seq', res)
        self.assertEqual(res['d_seq'], None)

    def test_put(self):

        _body = json.dumps({
            'd_bool': True,
            'd_int': 30,
            'd_float': 30.9,
            'd_list': [1, 2, 3, 4],
            'd_dict': {'1': 1, '2': 2, '3': 3, '4': 4},
            'd_dec': 25.10,
            'd_json': json.dumps({'5': 5, '6': 6, '7': 7, '8': 8}),
            'd_email': 'test@test.loc',
            'd_datetime': '2017-03-03 22:15:15',
            'd_date': '2017-03-03',
        })
        res = self.fetch('/api/hello', method='PUT', body=_body)

        self.assertEqual(res.code, 200)
        res = res.body.decode('utf-8')
        res = json.loads(res)

        self.assertIn('d_bool', res)
        self.assertEqual(res['d_bool'], True)
        self.assertIn('d_int', res)
        self.assertEqual(res['d_int'], 30)
        self.assertIn('d_float', res)
        self.assertEqual(res['d_float'], 30.9)
        self.assertIn('d_list', res)
        self.assertEqual(res['d_list'], [1, 2, 3, 4])
        self.assertIn('d_dict', res)
        self.assertEqual(res['d_dict'], {'1': 1, '2': 2, '3': 3, '4': 4})
        self.assertIn('d_dec', res)
        self.assertAlmostEqual(Decimal(res['d_dec']), Decimal('25.1'))
        self.assertIn('d_json', res)
        self.assertEqual(res['d_json'], {'5': 5, '6': 6, '7': 7, '8': 8})
        self.assertIn('d_email', res)
        self.assertEqual(res['d_email'], 'test@test.loc')
        self.assertIn('d_datetime', res)
        self.assertEqual(res['d_datetime'], '2017-03-03 22:15:15')
        self.assertIn('d_date', res)
        self.assertEqual(res['d_date'], '2017-03-03')
        self.assertIn('d_seq', res)
        self.assertEqual(res['d_seq'], None)

    def test_put_with_different_params_types(self):

        _body = json.dumps({
            'd_bool': 'test bool',
            'd_int': '20',
            'd_float': '20.8',
            'd_list': '[1, 2, 3, 4]',
            'd_dict': {'1': '1', '2': '2', '3': '3', '4': '4'},
            'd_dec': '25.10',
            'd_json': json.dumps([5, 6, 7, 8]),
            'd_email': 'test@test',
            'd_datetime': '2017-03-08 02:15:15',
            'd_date': '2017-03-08',
        })
        res = self.fetch('/api/hello', method='PUT', body=_body)

        self.assertEqual(res.code, 200)
        res = res.body.decode('utf-8')
        res = json.loads(res)

        self.assertIn('d_bool', res)
        self.assertEqual(res['d_bool'], False)
        self.assertIn('d_int', res)
        self.assertEqual(res['d_int'], 20)
        self.assertIn('d_float', res)
        self.assertEqual(res['d_float'], 20.8)
        self.assertIn('d_list', res)
        self.assertEqual(res['d_list'], [1, 2, 3, 4])
        self.assertIn('d_dict', res)
        self.assertEqual(res['d_dict'], {'1': '1', '2': '2', '3': '3', '4': '4'})
        self.assertIn('d_dec', res)
        self.assertEqual(res['d_dec'], '25.10')
        self.assertIn('d_json', res)
        self.assertEqual(res['d_json'], [5, 6, 7, 8])
        self.assertIn('d_email', res)
        self.assertEqual(res['d_email'], 'test@test')
        self.assertIn('d_datetime', res)
        self.assertEqual(res['d_datetime'], '2017-03-08 02:15:15')
        self.assertIn('d_date', res)
        self.assertEqual(res['d_date'], '2017-03-08')
        self.assertIn('d_seq', res)
        self.assertEqual(res['d_seq'], None)

    def test_put_with_wrong_list_param(self):

        _body = json.dumps({
            'd_bool': True,
            'd_int': 30,
            'd_float': 30.9,
            'd_list': 20,
            'd_dict': {'1': 1, '2': 2, '3': 3, '4': 4},
            'd_dec': 25.10,
            'd_json': json.dumps({'5': 5, '6': 6, '7': 7, '8': 8}),
            'd_email': 'test@test.loc',
            'd_datetime': '2017-03-03 22:15:15',
            'd_date': '2017-03-03',
        })
        res = self.fetch('/api/hello', method='PUT', body=_body)

        self.assertEqual(res.code, 400)
        res = res.body.decode('utf-8')
        res = json.loads(res)

        self.assertIn('message', res)
        self.assertEqual(res['message'], responses.lmap[responses.INVALID_REQUEST_ARGUMENT])

    def test_put_with_wrong_date_param(self):

        _body = json.dumps({
            'd_bool': True,
            'd_int': 30,
            'd_float': 30.9,
            'd_list': [1, 2, 3, 4],
            'd_dict': {'1': 1, '2': 2, '3': 3, '4': 4},
            'd_dec': 25.10,
            'd_json': json.dumps({'5': 5, '6': 6, '7': 7, '8': 8}),
            'd_email': 'test@test.loc',
            'd_datetime': '2017-03-03 22:15:15',
            'd_date': '2017-13-33',
        })
        res = self.fetch('/api/hello', method='PUT', body=_body)

        self.assertEqual(res.code, 400)
        res = res.body.decode('utf-8')
        res = json.loads(res)

        self.assertIn('message', res)
        self.assertEqual(res['message'], responses.lmap[responses.INVALID_REQUEST_ARGUMENT])

    def test_put_with_wrong_datetime_param(self):

        _body = json.dumps({
            'd_bool': True,
            'd_int': 30,
            'd_float': 30.9,
            'd_list': [1, 2, 3, 4],
            'd_dict': {'1': 1, '2': 2, '3': 3, '4': 4},
            'd_dec': 25.10,
            'd_json': json.dumps({'5': 5, '6': 6, '7': 7, '8': 8}),
            'd_email': 'test@test.loc',
            'd_datetime': '2017-13-33 22:15:15',
            'd_date': '2017-03-03',
        })
        res = self.fetch('/api/hello', method='PUT', body=_body)

        self.assertEqual(res.code, 400)
        res = res.body.decode('utf-8')
        res = json.loads(res)

        self.assertIn('message', res)
        self.assertEqual(res['message'], responses.lmap[responses.INVALID_REQUEST_ARGUMENT])

    def test_put_non_required_lower_int(self):

        _body = json.dumps({
            'd_bool': True,
            'd_int': 1,
            'd_float': 30.9,
            'd_list': [1, 2, 3, 4],
            'd_dict': {'1': 1, '2': 2, '3': 3, '4': 4},
            'd_dec': 25.10,
            'd_json': json.dumps({'5': 5, '6': 6, '7': 7, '8': 8}),
            'd_email': 'test@test.loc',
            'd_datetime': '2017-03-08 02:15:15',
            'd_date': '2017-03-03',
            'd_seq': 'udummyseqid',
        })
        res = self.fetch('/api/hello', method='PUT', body=_body)

        self.assertEqual(res.code, 400)
        res = res.body.decode('utf-8')
        res = json.loads(res)

        self.assertIn('message', res)
        self.assertEqual(res['message'], responses.lmap[responses.ARGUMENT_LOWER_THEN_MINIMUM])

    def test_put_non_required_higher_int(self):

        _body = json.dumps({
            'd_bool': True,
            'd_int': 900,
            'd_float': 30.9,
            'd_list': [1, 2, 3, 4],
            'd_dict': {'1': 1, '2': 2, '3': 3, '4': 4},
            'd_dec': 25.10,
            'd_json': json.dumps({'5': 5, '6': 6, '7': 7, '8': 8}),
            'd_email': 'test@test.loc',
            'd_datetime': '2017-03-08 02:15:15',
            'd_date': '2017-03-03',
            'd_seq': 'udummyseqid',
        })
        res = self.fetch('/api/hello', method='PUT', body=_body)

        self.assertEqual(res.code, 400)
        res = res.body.decode('utf-8')
        res = json.loads(res)

        self.assertIn('message', res)
        self.assertEqual(res['message'], responses.lmap[responses.ARGUMENT_HIGHER_THEN_MAXIMUM])

    def test_put_not_required_lower_float(self):

        _body = json.dumps({
            'd_bool': True,
            'd_int': 30,
            'd_float': 3.9,
            'd_list': [1, 2, 3, 4],
            'd_dict': {'1': 1, '2': 2, '3': 3, '4': 4},
            'd_dec': 25.10,
            'd_json': json.dumps({'5': 5, '6': 6, '7': 7, '8': 8}),
            'd_email': 'test@test.loc',
            'd_datetime': '2017-03-08 02:15:15',
            'd_date': '2017-03-03',
            'd_seq': 'udummyseqid',
        })
        res = self.fetch('/api/hello', method='PUT', body=_body)

        self.assertEqual(res.code, 400)
        res = res.body.decode('utf-8')
        res = json.loads(res)

        self.assertIn('message', res)
        self.assertEqual(res['message'], responses.lmap[responses.ARGUMENT_LOWER_THEN_MINIMUM])

    def test_put_non_required_higher_float(self):

        _body = json.dumps({
            'd_bool': True,
            'd_int': 30,
            'd_float': 130.9,
            'd_list': [1, 2, 3, 4],
            'd_dict': {'1': 1, '2': 2, '3': 3, '4': 4},
            'd_dec': 25.10,
            'd_json': json.dumps({'5': 5, '6': 6, '7': 7, '8': 8}),
            'd_email': 'test@test.loc',
            'd_datetime': '2017-03-08 02:15:15',
            'd_date': '2017-03-03',
            'd_seq': 'udummyseqid',
        })
        res = self.fetch('/api/hello', method='PUT', body=_body)

        self.assertEqual(res.code, 400)
        res = res.body.decode('utf-8')
        res = json.loads(res)

        self.assertIn('message', res)
        self.assertEqual(res['message'], responses.lmap[responses.ARGUMENT_HIGHER_THEN_MAXIMUM])

    def test_put_with_non_required_lower_list(self):

        _body = json.dumps({
            'd_bool': True,
            'd_int': 30,
            'd_float': 30.9,
            'd_list': [1, 2],
            'd_dict': {'1': 1, '2': 2, '3': 3, '4': 4},
            'd_dec': 25.10,
            'd_json': json.dumps({'5': 5, '6': 6, '7': 7, '8': 8}),
            'd_email': 'test@test.loc',
            'd_datetime': '2017-03-08 02:15:15',
            'd_date': '2017-03-03',
            'd_seq': 'udummyseqid',
        })
        res = self.fetch('/api/hello', method='PUT', body=_body)

        self.assertEqual(res.code, 400)
        res = res.body.decode('utf-8')
        res = json.loads(res)

        self.assertIn('message', res)
        self.assertEqual(res['message'], responses.lmap[responses.ARGUMENT_LOWER_THEN_MINIMUM])

    def test_put_with_non_required_higher_list(self):

        _body = json.dumps({
            'd_bool': True,
            'd_int': 30,
            'd_float': 30.9,
            'd_list': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
            'd_dict': {'1': 1, '2': 2, '3': 3, '4': 4},
            'd_dec': 25.10,
            'd_json': json.dumps({'5': 5, '6': 6, '7': 7, '8': 8}),
            'd_email': 'test@test.loc',
            'd_datetime': '2017-03-08 02:15:15',
            'd_date': '2017-03-03',
            'd_seq': 'udummyseqid',
        })
        res = self.fetch('/api/hello', method='PUT', body=_body)

        self.assertEqual(res.code, 400)
        res = res.body.decode('utf-8')
        res = json.loads(res)

        self.assertIn('message', res)
        self.assertEqual(res['message'], responses.lmap[responses.ARGUMENT_HIGHER_THEN_MAXIMUM])

    def test_put_with_non_required_lower_decimal(self):

        _body = json.dumps({
            'd_bool': True,
            'd_int': 30,
            'd_float': 30.9,
            'd_list': [1, 2, 3, 4],
            'd_dict': {'1': 1, '2': 2, '3': 3, '4': 4},
            'd_dec': 5.10,
            'd_json': json.dumps({'5': 5, '6': 6, '7': 7, '8': 8}),
            'd_email': 'test@test.loc',
            'd_datetime': '2017-03-08 02:15:15',
            'd_date': '2017-03-03',
            'd_seq': 'udummyseqid',
        })
        res = self.fetch('/api/hello', method='PUT', body=_body)

        self.assertEqual(res.code, 400)
        res = res.body.decode('utf-8')
        res = json.loads(res)

        self.assertIn('message', res)
        self.assertEqual(res['message'], responses.lmap[responses.ARGUMENT_LOWER_THEN_MINIMUM])

    def test_put_with_non_required_higher_decimal(self):

        _body = json.dumps({
            'd_bool': True,
            'd_int': 30,
            'd_float': 30.9,
            'd_list': [1, 2, 3, 4],
            'd_dict': {'1': 1, '2': 2, '3': 3, '4': 4},
            'd_dec': 65.10,
            'd_json': json.dumps({'5': 5, '6': 6, '7': 7, '8': 8}),
            'd_email': 'test@test.loc',
            'd_datetime': '2017-03-08 02:15:15',
            'd_date': '2017-03-03',
            'd_seq': 'udummyseqid',
        })
        res = self.fetch('/api/hello', method='PUT', body=_body)

        self.assertEqual(res.code, 400)
        res = res.body.decode('utf-8')
        res = json.loads(res)

        self.assertIn('message', res)
        self.assertEqual(res['message'], responses.lmap[responses.ARGUMENT_HIGHER_THEN_MAXIMUM])

    def test_put_with_non_required_lower_datetime(self):

        _body = json.dumps({
            'd_bool': True,
            'd_int': 30,
            'd_float': 30.9,
            'd_list': [1, 2, 3, 4],
            'd_dict': {'1': 1, '2': 2, '3': 3, '4': 4},
            'd_dec': 25.10,
            'd_json': json.dumps({'5': 5, '6': 6, '7': 7, '8': 8}),
            'd_email': 'test@test.loc',
            'd_datetime': '2017-03-01 22:15:15',
            'd_date': '2017-03-03',
            'd_seq': 'udummyseqid',
        })
        res = self.fetch('/api/hello', method='PUT', body=_body)

        self.assertEqual(res.code, 400)
        res = res.body.decode('utf-8')
        res = json.loads(res)

        self.assertIn('message', res)
        self.assertEqual(res['message'], responses.lmap[responses.ARGUMENT_LOWER_THEN_MINIMUM])

    def test_put_with_non_required_higher_datetime(self):

        _body = json.dumps({
            'd_bool': True,
            'd_int': 30,
            'd_float': 30.9,
            'd_list': [1, 2, 3, 4],
            'd_dict': {'1': 1, '2': 2, '3': 3, '4': 4},
            'd_dec': 25.10,
            'd_json': json.dumps({'5': 5, '6': 6, '7': 7, '8': 8}),
            'd_email': 'test@test.loc',
            'd_datetime': '2017-03-11 22:15:15',
            'd_date': '2017-03-03',
            'd_seq': 'udummyseqid',
        })
        res = self.fetch('/api/hello', method='PUT', body=_body)

        self.assertEqual(res.code, 400)
        res = res.body.decode('utf-8')
        res = json.loads(res)

        self.assertIn('message', res)
        self.assertEqual(res['message'], responses.lmap[responses.ARGUMENT_HIGHER_THEN_MAXIMUM])

    def test_put_with_non_required_lower_date(self):

        _body = json.dumps({
            'd_bool': True,
            'd_int': 30,
            'd_float': 30.9,
            'd_list': [1, 2, 3, 4],
            'd_dict': {'1': 1, '2': 2, '3': 3, '4': 4},
            'd_dec': 25.10,
            'd_json': json.dumps({'5': 5, '6': 6, '7': 7, '8': 8}),
            'd_email': 'test@test.loc',
            'd_datetime': '2017-03-03 22:15:15',
            'd_date': '2017-03-01',
            'd_seq': 'udummyseqid',
        })
        res = self.fetch('/api/hello', method='PUT', body=_body)

        self.assertEqual(res.code, 400)
        res = res.body.decode('utf-8')
        res = json.loads(res)

        self.assertIn('message', res)
        self.assertEqual(res['message'], responses.lmap[responses.ARGUMENT_LOWER_THEN_MINIMUM])

    def test_put_with_non_required_higher_date(self):

        _body = json.dumps({
            'd_bool': True,
            'd_int': 30,
            'd_float': 30.9,
            'd_list': [1, 2, 3, 4],
            'd_dict': {'1': 1, '2': 2, '3': 3, '4': 4},
            'd_dec': 25.10,
            'd_json': json.dumps({'5': 5, '6': 6, '7': 7, '8': 8}),
            'd_email': 'test@test.loc',
            'd_datetime': '2017-03-03 22:15:15',
            'd_date': '2017-03-11',
            'd_seq': 'udummyseqid',
        })
        res = self.fetch('/api/hello', method='PUT', body=_body)

        self.assertEqual(res.code, 400)
        res = res.body.decode('utf-8')
        res = json.loads(res)

        self.assertIn('message', res)
        self.assertEqual(res['message'], responses.lmap[responses.ARGUMENT_HIGHER_THEN_MAXIMUM])

    def test_post(self):

        res = self.fetch('/api/hello', method='POST', body='')

        self.assertEqual(res.code, 200)
        res = res.body.decode('utf-8')
        res = json.loads(res)

        self.assertIn('message', res)
        self.assertEqual(res['message'], 'hello post')

    def test_patch(self):

        res = self.fetch('/api/hello', method='PATCH', body='')

        self.assertEqual(res.code, 200)
        res = res.body.decode('utf-8')
        res = json.loads(res)

        self.assertIn('message', res)
        self.assertEqual(res['message'], 'hello patch')

    def test_delete(self):

        res = self.fetch('/api/hello', method='DELETE')

        self.assertEqual(res.code, 200)
        res = res.body.decode('utf-8')
        res = json.loads(res)

        self.assertIn('message', res)
        self.assertEqual(res['message'], 'hello delete')


class TestHelloWorld(TestBase):

    def test_get(self):

        import src.lookup.languages as languages

        _url = '/api/{}/hello'.format(languages.lmap[languages.EN])
        res = self.fetch(_url)
        self.assertEqual(res.code, 200)
        res = res.body.decode('utf-8')
        res = json.loads(res)
        self.assertIn('hello', res)
        self.assertEqual(res['hello'], 'hello world')

        _url = '/api/{}/hello'.format(languages.lmap[languages.RS])
        res = self.fetch(_url)
        self.assertEqual(res.code, 200)
        res = res.body.decode('utf-8')
        res = json.loads(res)
        self.assertIn('hello', res)
        self.assertEqual(res['hello'], 'pozdrav svima')

        _url = '/api/{}/hello'.format(languages.lmap[languages.DE])
        res = self.fetch(_url)
        self.assertEqual(res.code, 200)
        res = res.body.decode('utf-8')
        res = json.loads(res)
        self.assertIn('hello', res)
        self.assertEqual(res['hello'], 'hallo welt')

    def test_non_existing_language(self):

        import src.lookup.languages as languages

        _dummy_lang = 'dl'
        self.assertNotIn(_dummy_lang, languages.lrev)
        _url = '/api/{}/hello'.format(_dummy_lang)
        res = self.fetch(_url)
        self.assertEqual(res.code, 400)
        res = res.body.decode('utf-8')
        res = json.loads(res)
        self.assertIn('message', res)
        self.assertEqual(res['message'], responses.lmap[responses.GET_NOT_FOUND])

