# -*- coding: utf-8 -*-

"""
Echo API title
:description:
echo api description
"""

import json
import datetime
import base_common.msg
import base_common.msg
from base_common.dbacommon import params
from base_common.dbacommon import app_api_method
from base_config.service import log


name = "echo"
location = "echo"
request_timeout = 10


@app_api_method(
    method='GET',
    api_return=[(200, 'echoed message'), (404, '')]
)
@params(
    {'arg': 'message', 'type': str, 'required': True, 'description': 'echo parametar description','example':'echo mockup example'}
)
def do_get(message, **kwargs):
    """
    Get method of echo API call - title
    :description:
    Get method of echo API call - description

    """
    return base_common.msg.get_ok({'echo': message})
    return {'echo': 'get echo'}


@app_api_method(
    method='PUT',
    api_return=[(200, 'echo date'), (400, ''), (401, 'Unauthorized')]
)
@params(
    {'arg': 'message', 'type': datetime.date, 'required': True, 'description': 'echo parametar description','example':'echo mockup example'}
)
def do_put(message, **kwargs):
    """
    Put method of echo API call - title
    :description:
    Put method of echo API call - description

    """

    log.info('echo.put')

    #return base_common.msg.put_ok()
    return base_common.msg.put_ok({'echo': str(message)})
    return base_common.msg.put_ok({'echo': str(message)}, http_status=202)


@app_api_method(
    method='DELETE',
    api_return=[(200, 'echo date'), (400, ''), (401, 'Unauthorized')]
)
@params(
    {'arg': 'message', 'type': datetime.datetime, 'required': True, 'description': 'echo parametar description','example':'echo mockup example'}
)
def do_delete(message, **kwargs):
    """
    Delete method of echo API call - title
    :description:
    Delete method of echo API call - description

    """

    log.info('echo.do_delete')

    return base_common.msg.delete_ok({'echo': str(message)})
    return base_common.msg.delete_ok({'echo': 'delete echo'}, http_status=202)


@app_api_method(
    method='POST',
    api_return=[(200, 'echo date'), (400, ''), (401, 'Unauthorized')]
)
@params(
    {'arg': 'message', 'type': json, 'required': True, 'description': 'description za parametar'}
)
def do_post(message, **kwargs):
    """
    Post method of echo API call - title
    :description:
    Post method of echo API call - description

    """

    log.info('echo.do_post')

    return base_common.msg.post_ok({'echo': message})
    return base_common.msg.post_ok({'echo': message}, http_status=201)


@app_api_method(
    method='PATCH',
    api_return=[(200, 'echo date'), (400, '')]
)
@params(
    {'arg': 'message', 'type': int, 'required': True, 'description': 'description za parametar'}
)
def do_patch(message, **kwargs):
    """
    Patch method of echo API call - title
    :description:
    Patch method of echo API call - description

    """

    log.info('echo.do_patch')

    # return base_common.msg.put_ok()
    return base_common.msg.patch_ok({'echo': message})
    return base_common.msg.patch_ok({'echo': message}, http_status=201)


