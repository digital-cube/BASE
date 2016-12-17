# coding= utf-8

import json

import base.application.lookup.responses as msgs
from base.common.utils import log
from base.application.components import Base
from base.application.components import api
from base.application.components import params
from base.application.components import authenticated
from base.application.helpers.exceptions import SaveHash2ParamsException


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
        try:
            _res = api_hooks.save_hash(hash_data)
        except SaveHash2ParamsException as e:
            log.critical(str(e))
            return self.error(msgs.SAVE_HASH_PARAMS_ERROR)

        return self.ok(_res)

