 # -*- coding: utf-8 -*-

"""
Get params for worker options
"""

import json
import datetime
import base_common.msg
from base_lookup import api_messages as msgs
from base_config.service import log
from base_config.settings import MAIL_CHANNEL
from base_common.dbacommon import params
from base_common.dbacommon import app_api_method
from base_common.dbacommon import get_db
from base_common.dbacommon import get_redis_db
import base_common.app_hooks as apphooks

name = "Params"
location = "params"
request_timeout = 10

@app_api_method(
    method='GET'
)
@params()
def get_params(**kwargs):

    res = {}

    if hasattr(apphooks, 'get_params'):
        get_params_res = apphooks.get_params()
        if get_params_res == False:
            log.critical('Error getting params')
            return base_common.msg.error('ERROR')

        if isinstance(get_params_res, dict):
            res.update(get_params_res)

    return base_common.msg.ok(res)