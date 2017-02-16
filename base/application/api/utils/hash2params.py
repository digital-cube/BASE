# coding= utf-8

import json

import base.application.lookup.responses as msgs
from base.application.components import Base
from base.application.components import api
from base.application.components import authenticated
from base.application.components import params
from base.application.helpers.exceptions import GetHash2ParamsException
from base.application.helpers.exceptions import SaveHash2ParamsException
from base.common.utils import log


@authenticated()
@api(
    URI='/tools/h2p',
    PREFIX=False)
class Hash2Params(Base):

    @params(
        {'name': 'data', 'type': json, 'required': True,  'doc': 'hash data'},
    )
    def put(self, hash_data):
        """Save data with hash"""

        from base.application.api_hooks import api_hooks
        try:
            _res = api_hooks.save_hash(hash_data)
        except SaveHash2ParamsException as e:
            log.critical(str(e))
            return self.error(msgs.SAVE_HASH_PARAMS_ERROR)

        return self.ok(_res)


@authenticated()
@api(
    URI='/tools/h2p/:h2p',
    PREFIX=False,
    SPECIFICATION_PATH='Hash2Params')
class Hash2ParamsGet(Base):

    @params(
        {'name': 'h2p', 'type': str, 'required': True,  'doc': 'hash to get data from'},
    )
    def get(self, h2p):
        """Get data from hash"""

        from base.application.api_hooks import api_hooks
        try:
            _res = api_hooks.get_hash_data(h2p)
        except GetHash2ParamsException as e:
            log.critical(str(e))
            return self.error(msgs.GET_HASH_PARAMS_ERROR)

        return self.ok(_res)
