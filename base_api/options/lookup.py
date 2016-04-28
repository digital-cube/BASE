"""
Lookup
:description:
Get application's lookup maps
"""

import base_common.msg
from base_common.dbacommon import params
from base_common.dbacommon import authenticated_call
from base_common.dbacommon import app_api_method
import base_common.app_hooks as apphooks
from base_lookup import api_messages as msgs
from base_config.service import log

name = "Lookup"
location = "lookup"
request_timeout = 10


# @authenticated_call()
@app_api_method(
    method='GET',
    api_return=[(200, ''), (404, '')]
)
@params()
def get_lookups(**kwargs):
    """
    Get lookups
    """

    res = {}

    if hasattr(apphooks, 'pack_lookups'):
        _pck_lkp_res = apphooks.pack_lookups()
        if _pck_lkp_res == False:
            log.critical('Error pack lookups')
            return base_common.msg.error(msgs.ERROR_POST_CHECK)

        if isinstance(_pck_lkp_res, dict):
            res.update(_pck_lkp_res)

    return base_common.msg.get_ok(res)

