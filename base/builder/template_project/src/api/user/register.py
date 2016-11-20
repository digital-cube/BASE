# coding= utf-8

import json
from base.application.components import Base
from base.application.components import api
from base.application.components import params


@api(
    URI='/register',
    PREFIX=False)
class Register(Base):

    @params(
        {'name': 'username', 'type': 'e-mail', 'required': True,  'doc': 'username to register'},
        {'name': 'password', 'type': str, 'required': True,  'doc': "user's password"},
        {'name': 'data', 'type': json, 'required': True,  'doc': "user's additional data"},
    )
    def post(self, username, password, data):
        return self.ok('register ok')
