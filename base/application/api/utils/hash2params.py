# coding= utf-8

import json

from base.application.components import Base
from base.application.components import api
from base.application.components import params
from base.application.components import authenticated


@authenticated()
@api(
    URI='/h2p',
    PREFIX=False)
class Hash2Params(Base):

    def get(self):
        return self.ok('get h2p')

    @params(
        {'name': 'data', 'type': json, 'required': True,  'doc': 'hash data'},
    )
    def put(self, hash_data):

        from base.application.api import api_hooks

        # todo: get self.auth_user - make it in Base class
        user = None
        _res = api_hooks.save_hash(hash_data, user)
        return self.ok('get h2p')

