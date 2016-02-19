"""
Echo mockup API module
"""

import json
import datetime
import base_common.msg
import base_common.msg
from base_common.dbacommon import params
from base_common.dbacommon import app_api_method


name = "echo"
location = "echo"
request_timeout = 10


@app_api_method
@params(
    {'arg': 'message', 'type': str, 'required': True}
)
def do_get(request, *args, **kwargs):
    """
    Get method of echo API call - test
    :param echo_string: token given in request uri, string, True
    :return: 200, OK
    :return: 404, not found
    """

    message, = args

    #request.log.info('echo.get')
    return base_common.msg.get_ok({'echo': message})
    return {'echo': 'get echo'}


@app_api_method
@params(
    {'arg': 'message', 'type': datetime.date, 'required': True}
)
def do_put(_, *args, **kwargs):
    """
    Put method of echo API call - test
    :param echo_string:  insert test string, string, True
    :return:  200, echo
    :return:  202, echo to be accepted
    :return:  204
    :return:  400, bad request
    :return:  401, Unauthorized
    """

    dt, = args
    log = _.log
    log.info('echo.put')

    #return base_common.msg.put_ok()
    return base_common.msg.put_ok({'echo': str(dt)})
    return base_common.msg.put_ok({'echo': str(dt)}, http_status=202)


@app_api_method
@params(
    {'arg': 'message', 'type': datetime.datetime, 'required': True}
)
def do_delete(_ , *args, **kwargs):
    """
    Delete method of echo API call - test
    :param echo_string: delete test string, string, True
    :return:  200, OK
    :return:  202, echo to be deleted
    :return:  204
    :return:  400, bad request
    :return:  401, Unauthorized
    """

    dt, = args

    log = _.log
    log.info('echo.do_delete')

    return base_common.msg.delete_ok({'echo': str(dt)})
    return base_common.msg.delete_ok({'echo': 'delete echo'}, http_status=202)


@app_api_method
@params(
    {'arg': 'message', 'type': json, 'required': True}
)
def do_post(request, *args, **kwargs):
    """
    Post method of echo API call - test
    :param echo_string: insert test string, string, True
    :return:  200, OK
    :return:  201, echo created
    :return:  204
    """

    j, = args
    request.log.info('echo.do_post')

    return base_common.msg.post_ok({'echo': j})
    return base_common.msg.post_ok({'echo': j}, http_status=201)


@app_api_method
@params(
    {'arg': 'message', 'type': int, 'required': True}
)
def do_patch(request, *args, **kwargs):
    """
    Patch method of echo API call - test
    :param echo_string: echo int, int, True
    :return:  200, OK
    :return:  201, echo created
    :return:  204
    """

    i, = args
    request.log.info('echo.do_patch')

    # return base_common.msg.put_ok()
    return base_common.msg.patch_ok({'echo': i})
    return base_common.msg.patch_ok({'echo': i}, http_status=201)


def test():

    import base_common.test

    request = base_common.test.Request()
    request.set_argument('message', 'test')

    result = do_post(request)
    print(result)


def svc_test():

    print(call({'message': 'test'}))


if __name__ == "__main__":

    test()
