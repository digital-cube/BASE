import os
import sys

pth = os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))
sys.path.append(pth)

from base_svc.comm import call
import base_lookup.api_messages as amsgs


class Color:
    BLUE = '\033[0;34m'
    BOLD_BLUE = '\033[1;34m'
    GREEN = '\033[0;92m'
    BOLD_GREEN = '\033[1;92m'
    RED = '\033[0;31m'
    BOLD_RED = '\033[1;31m'
    YELLOW = '\033[0;93m'
    BOLD_YELLOW = '\033[1;93m'
    DEFAULT = '\033[0m'


def test_warning(loc, method, result):
    print(Color.BOLD_YELLOW, 'WARNING', loc, method, '-> {}'.format(result) if result else '', Color.DEFAULT)


def test_failed(loc, method, result):
    print(Color.BOLD_RED, 'FAILED', loc, method, '->', result, Color.DEFAULT)


def test_passed(loc, method, result):
    print(Color.BOLD_GREEN, 'PASSED', loc, method, '-> {}'.format(result) if result else '', Color.DEFAULT)


def test_db_active():
    return True


def do_test(svc_port, location, method, token, data, expected_status, expected_data, result):

    _headers = None
    if token:
        _headers = {'Authorization': token}

    res, status = call('localhost', svc_port, location, data, method, call_headers=_headers)
    result.update({'res': res, 'status': status})
    res = json.loads(res) if res else {}
    # print('R',result)
    # print('R', res, type(res))

    if status != expected_status:
        return False

    if expected_data:
        for k in expected_data:

            if k not in res:
                return False

            if expected_data[k] != res[k]:
                test_warning(location, method, '{}: {} | expected | {}'.format(k, expected_data[k],res[k]))

    return True


def test(svc_port, location, method, token, data, expected_status, expected_data, __result):

    if not test_db_active():
        test_failed('TEST DATABASE NOT ACTIVE', '', '')
        sys.exit(1)

    if not do_test(svc_port, location, method, token, data, expected_status, expected_data, __result):
        test_failed(location, method, __result)
        sys.exit(1)

    test_passed(location, method, __result)


def insert_path_to_sys():

    import os
    pth = os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))
    print(pth)
    sys.path.append(pth)


if __name__ == '__main__':

    import json
    from base_common.importer import import_from_settings
    from base_common.importer import get_installed_apps

    # insert_path_to_sys()

    imported_modules = []
    installed_apps = {}

    get_installed_apps(installed_apps)

    app = sys.argv[1]

    svc_port = installed_apps[app]['svc_port']
    import_from_settings(imported_modules, app)

    result = {}

    # REGISTER TESTS # TODO: PROBLEM WITH IMPORT REGISTRATION QUERY
    import base_api.users.user_register
    test(
        svc_port=svc_port,
        location=base_api.users.user_register.location,
        method='GET',
        token=None,
        data={'username':'user1','password':'123'},
        expected_status=404,
        expected_data={'message':'GET not implemented'},
        # expected_data={'message':amsgs.msgs[amsgs.USERNAME_ALREADY_TAKEN]},
        __result=result)

    # test(
    #     svc_port=svc_port,
    #     location=base_api.users.user_register.location,
    #     method='POST',
    #     token=None,
    #     data={'username':'user1','password':'123'},
    #     expected_status=200,
    #     expected_data={'params':amsgs.msgs[amsgs.USERNAME_ALREADY_TAKEN]},
    #     # expected_data={'message':amsgs.msgs[amsgs.USERNAME_ALREADY_TAKEN]},
    #     __result=result)

    # LOGIN TESTS
    import base_api.users.user_login
    test(
        svc_port=svc_port,
        location=base_api.users.user_login.location,
        method='POST',
        token=None,
        data={'username':'user2','password':'123'},
        expected_status=200,
        expected_data={'params': {}},
        __result=result)

    res = result['res']
    res = json.loads(res)
    tk = res['params']['token']

    test(
        svc_port=svc_port,
        location=base_api.users.user_login.location,
        method='POST',
        token=None,
        data={'username':'no_user','password':'123'},
        expected_status=400,
        expected_data={'message':amsgs.msgs[amsgs.USER_NOT_FOUND]},
        __result=result)
    test(
        svc_port=svc_port,
        location=base_api.users.user_login.location,
        method='POST',
        token=None,
        data={'userna':'no_user','password':'123'},
        expected_status=400,
        expected_data={'message':amsgs.msgs[amsgs.MISSING_REQUEST_ARGUMENT]},
        __result=result)
    test(
        svc_port=svc_port,
        location=base_api.users.user_login.location,
        method='POST',
        token=None,
        data={'username':'no_user','passwo':'123'},
        expected_status=400,
        expected_data={'message':amsgs.msgs[amsgs.MISSING_REQUEST_ARGUMENT]},
        __result=result)

    # LOGOUT TESTS
    import base_api.users.user_logout
    test(
        svc_port=svc_port,
        location=base_api.users.user_logout.location,
        method='POST',
        token=None,
        data={},
        expected_status=400,
        expected_data={'message':amsgs.msgs[amsgs.UNAUTHORIZED_REQUEST]},
        __result=result)
    test(
        svc_port=svc_port,
        location=base_api.users.user_logout.location,
        method='POST',
        token=tk,
        data={},
        expected_status=204,
        expected_data={},
        __result=result)

    # FORGOT PASSWORD TESTS
    import base_api.users.forgot_password
    test(
        svc_port=svc_port,
        location=base_api.users.forgot_password.location,
        method='POST',
        token=None,
        data={'ername':'user2'},
        expected_status=404,
        expected_data={'message': 'POST not implemented'},
        __result=result)
    test(
        svc_port=svc_port,
        location=base_api.users.forgot_password.location,
        method='PUT',
        token=None,
        data={'ername':'user2'},
        expected_status=400,
        expected_data={'message': amsgs.msgs[amsgs.MISSING_REQUEST_ARGUMENT]},
        __result=result)
    test(
        svc_port=svc_port,
        location=base_api.users.forgot_password.location,
        method='PUT',
        token=None,
        data={'username':'user2'},
        expected_status=200,
        expected_data={},
        __result=result)

    # HASHING PARAMETERS TESTS
    import base_api.hash2params.save_hash
    test(
        svc_port=svc_port,
        location=base_api.hash2params.save_hash.location,
        method='POST',
        token=None,
        data={'username':'user2','password':'123'},
        expected_status=404,
        expected_data={'message': 'POST not implemented'},
        __result=result)
    test(
        svc_port=svc_port,
        location=base_api.hash2params.save_hash.location,
        method='PUT',
        token=None,
        data={'dat':'user2'},
        expected_status=400,
        expected_data={'message': amsgs.msgs[amsgs.MISSING_REQUEST_ARGUMENT]},
        __result=result)
    test(
        svc_port=svc_port,
        location=base_api.hash2params.save_hash.location,
        method='PUT',
        token=None,
        data={'data': {'username':'user2'}},
        expected_status=200,
        expected_data={},
        __result=result)
    res = result['res']
    res = json.loads(res)
    htk = res['params']['h']

    # CHANGE PASSWORD TESTS
    import base_api.users.change_password
    test(
        svc_port=svc_port,
        location=base_api.users.user_login.location,
        method='POST',
        token=None,
        data={'username':'user2','password':'123'},
        expected_status=200,
        expected_data={'params': {}},
        __result=result)

    res = result['res']
    res = json.loads(res)
    tk = res['params']['token']

    test(
        svc_port=svc_port,
        location=base_api.users.change_password.location,
        method='POST',
        token=None,
        data={'ername':'user2'},
        expected_status=400,
        expected_data={'message': amsgs.msgs[amsgs.MISSING_REQUEST_ARGUMENT]},
        __result=result)
    test(
        svc_port=svc_port,
        location=base_api.users.change_password.location,
        method='POST',
        token=tk,
        data={'newpassword':'123'},
        expected_status=400,
        expected_data={'message': amsgs.msgs[amsgs.MISSING_REQUEST_ARGUMENT]},
        __result=result)
    test(
        svc_port=svc_port,
        location=base_api.users.change_password.location,
        method='POST',
        token=tk,
        data={'newpassword':'123','oldpassword':'123'},
        expected_status=200,
        expected_data={'params': {}},
        __result=result)

    # TODO: finish this one
    # loc = base_api.users.change_password.location[:-2] + '/' + htk
    # test(
    #     svc_port=svc_port,
    #     location=loc,
    #     method='POST',
    #     token=None,
    #     data={'newpassword':'123'},
    #     expected_status=200,
    #     expected_data={'params': {}},
    #     __result=result)

    # CHECK USER TESTS
    import base_api.users.user_check
    test(
        svc_port=svc_port,
        location=base_api.users.user_check.location,
        method='POST',
        token=None,
        data={'username':'user2','password':'123'},
        expected_status=400,
        expected_data={'message': amsgs.msgs[amsgs.UNAUTHORIZED_REQUEST]},
        __result=result)
    test(
        svc_port=svc_port,
        location=base_api.users.user_check.location,
        method='POST',
        token=tk,
        data={'username':'user2','password':'123'},
        expected_status=200,
        expected_data={'params': {}},
        __result=result)

