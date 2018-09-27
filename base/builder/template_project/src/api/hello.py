# coding= utf-8

from base.application.components import Base
from base.application.components import api
from base.application.components import params
from base.application.components import authenticated

import datetime
import decimal
import json


# @authenticated()  # if every http method has to be authenticated
@api(
    URI='/:__LANG__/hello',
    SPECIFICATION_PATH='hello', # optional path for specification list
    # PREFIX=False, # if missing or True uri will be /_prefix_/hello
)
class HelloWorld(Base):
    # @authenticated()  # if get method has to be authenticated
    @params(  # if you want to add params
        {'name': 'language', 'type': str, 'doc': 'dummy sequencer'},
    )
    def get(self, language):
        """HelloWorld - get"""

        from src.lookup import languages

        _message = 'hello world'
        if language in languages.lrev:
            if languages.lrev[language] == languages.EN:
                _message = 'hello world'
            if languages.lrev[language] == languages.RS:
                _message = 'pozdrav svima'
            if languages.lrev[language] == languages.DE:
                _message = 'hallo welt'

        return self.ok({'hello': _message})


# @authenticated()  # if every http method has to be authenticated
@api(
    URI='/hello',
    # SPECIFICATION_PATH='hello', # optional path for specification list
    # PREFIX=False, # if missing or True uri will be /_prefix_/hello
)
class Hello(Base):
    # @authenticated()  # if get method has to be authenticated
    @params(  # if you want to add params
        {'name': 'd_bool', 'type': bool, 'doc': 'dummy bool', 'required': False},
        {'name': 'd_int', 'type': int, 'doc': 'dummy int', 'min': 10, 'max': 100, 'required': False},
        {'name': 'd_float', 'type': float, 'doc': 'dummy float', 'min': 10.01, 'max': 100.01, 'required': False},
        {'name': 'd_list', 'type': list, 'doc': 'dummy list', 'min': 3, 'max': 10, 'required': False},
        {'name': 'd_dict', 'type': dict, 'doc': 'dummy dict', 'required': False},
        {'name': 'd_dec', 'type': decimal.Decimal, 'doc': 'dummy dec', 'min': 10.3, 'max': 30.2, 'required': False},
        {'name': 'd_json', 'type': json, 'doc': 'dummy json', 'required': False},
        {'name': 'd_email', 'type': 'e-mail', 'doc': 'dummy e-mail', 'required': False},
        {'name': 'd_datetime', 'type': datetime.datetime, 'doc': 'dummy datetime', 'min': '2017-03-02 17:22:23',
         'max': '2017-03-10 22:18:23', 'required': False},
        {'name': 'd_date', 'type': datetime.date, 'doc': 'dummy date', 'min': '2017-03-02', 'max': '2017-03-10',
         'required': False},
        {'name': 'd_seq', 'type': 'sequencer:s_users:u', 'doc': 'dummy sequencer', 'required': False},
    )
    def get(self, d_bool, d_int, d_float, d_list, d_dict, d_dec, d_json, d_email, d_datetime, d_date, d_seq):
        """Hello - get"""
        return self.ok({
            'd_bool': d_bool,
            'd_int': d_int,
            'd_float': d_float,
            'd_list': d_list,
            'd_dict': d_dict,
            'd_dec': str(d_dec),
            'd_json': d_json,
            'd_email': d_email,
            'd_datetime': str(d_datetime),
            'd_date': str(d_date),
            'd_seq': d_seq,
        })

    # @authenticated()  # if put method has to be authenticated
    @params(  # if you want to add params
        {'name': 'd_bool', 'type': bool, 'required': False, 'doc': 'dummy bool'},
        {'name': 'd_int', 'type': int, 'required': False, 'doc': 'dummy int', 'min': 10, 'max': 100},
        {'name': 'd_float', 'type': float, 'required': False, 'doc': 'dummy float', 'min': 10.01, 'max': 100.01},
        {'name': 'd_list', 'type': list, 'required': False, 'doc': 'dummy list', 'min': 3, 'max': 10},
        {'name': 'd_dict', 'type': dict, 'required': False, 'doc': 'dummy dict'},
        {'name': 'd_dec', 'type': decimal.Decimal, 'required': False, 'doc': 'dummy dec', 'min': 10.3, 'max': 30.2},
        {'name': 'd_json', 'type': json, 'required': False, 'doc': 'dummy json'},
        {'name': 'd_email', 'type': 'e-mail', 'required': False, 'doc': 'dummy e-mail'},
        {'name': 'd_datetime', 'type': datetime.datetime, 'required': False, 'doc': 'dummy datetime',
         'min': '2017-03-02 17:22:23', 'max': '2017-03-10 22:18:23'},
        {'name': 'd_date', 'type': datetime.date, 'required': False, 'doc': 'dummy date', 'min': '2017-03-02',
         'max': '2017-03-10'},
        {'name': 'd_seq', 'type': 'sequencer:s_users:u', 'required': False, 'doc': 'dummy sequencer'},
    )
    def put(self, d_bool, d_int, d_float, d_list, d_dict, d_dec, d_json, d_email, d_datetime, d_date, d_seq):
        """Hello - put"""
        return self.ok({
            'd_bool': d_bool,
            'd_int': d_int,
            'd_float': d_float,
            'd_list': d_list,
            'd_dict': d_dict,
            'd_dec': str(d_dec) if d_dec is not None else None,
            'd_json': d_json,
            'd_email': d_email,
            'd_datetime': str(d_datetime) if d_datetime is not None else None,
            'd_date': str(d_date) if d_date is not None else None,
            'd_seq': d_seq,
        })

    # @authenticated()  # if post method has to be authenticated
    # TODO url testing
    def post(self):
        """Hello - post"""
        return self.ok('hello post')

    # @authenticated()  # if patch method has to be authenticated
    # TODO default params testing
    def patch(self):
        """Hello - patch"""
        return self.ok('hello patch')

    # @authenticated()  # if delete method has to be authenticated
    def delete(self):
        """Hello - delete"""
        return self.ok('hello delete')

