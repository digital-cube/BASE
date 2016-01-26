"""
Echo mockup API module
"""

import base_common.msg
from base_common.dbacommon import app_api_method


name = "echo"
location = "echo"
request_timeout = 10


@app_api_method
def do_get(request, *args, **kwargs):
    """
    Get method of echo API call - test
    :param echo_string: token given in request uri, string, True
    :return: 200, OK
    :return: 404, not found
    """

    request.log.info('echo.get')
    return base_common.msg.get_ok({'echo': 'get echo'})
    return {'echo': 'get echo'}


@app_api_method
def do_put(request, *args, **kwargs):
    """
    Put method of echo API call - test
    :param echo_string:  insert test string, string, True
    :return:  200, echo
    :return:  202, echo to be accepted
    :return:  204
    :return:  400, bad request
    :return:  401, Unauthorized
    """

    request.log.info('echo.put')
    print('PUT CONTENT')
    return base_common.msg.put_ok()
    return base_common.msg.put_ok({'echo': 'put echo'})
    return base_common.msg.put_ok({'echo': 'put echo'}, http_status=202)


@app_api_method
def do_delete(request, *args, **kwargs):
    """
    Delete method of echo API call - test
    :param echo_string: delete test string, string, True
    :param timeout: timeout for delete test string, string, False
    :return:  200, OK
    :return:  202, echo to be deleted
    :return:  204
    :return:  400, bad request
    :return:  401, Unauthorized
    """

    request.log.info('echo.do_delete')
    print('DELETE CONTENT')

    return base_common.msg.put_ok()
    return base_common.msg.put_ok({'echo': 'delete echo'})
    return base_common.msg.put_ok({'echo': 'delete echo'}, http_status=202)


@app_api_method
def do_post(request, *args, **kwargs):
    """
    Post method of echo API call - test
    :param echo_string: insert test string, string, True
    :return:  200, OK
    :return:  201, echo created
    :return:  204
    """

    logged_user_dict = kwargs['logged_user_dict']
    request.log.info('echo.do_post')

    return base_common.msg.put_ok()
    return base_common.msg.put_ok({'echo': 2 * request.get_argument('message'), 'logged_user_dict': logged_user_dict})
    return base_common.msg.put_ok({'echo': 2 * request.get_argument('message'), 'logged_user_dict': logged_user_dict}, http_status=201)


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
