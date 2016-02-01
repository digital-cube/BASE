import os
import sys

pth = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
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


class WarningLevel:
    NO_WARNING = 0
    STRICT = 1  # DEFAULT
    STRICT_ON_KEY = 2  # ONLY KEY HAS TO BE CHECKED


def test_warning(loc, method, result):
    print(Color.BOLD_YELLOW, 'WARNING', loc, method, '-> {}'.format(result) if result else '', Color.DEFAULT)


def test_failed(loc, method, result):
    print(Color.BOLD_RED, 'FAILED', loc, method, '->', result, Color.DEFAULT)


def test_passed(loc, method, result):
    print(Color.BOLD_GREEN, 'PASSED', loc, method, '-> {}'.format(result) if result else '', Color.DEFAULT)


def test_db_active():
    return True


def do_test(svc_port, location, method, token, data, expected_status, expected_data, result, warning_level):
    _headers = None
    if token:
        _headers = {'Authorization': token}

    res, status = call('localhost', svc_port, location, data, method, call_headers=_headers)
    res = json.loads(res) if res else {}
    res.update({'status': status})
    result.update(res)

    if status != expected_status:
        return False

    if expected_data:
        for k in expected_data:

            if k not in res and warning_level != WarningLevel.NO_WARNING:
                return False

            if expected_data[k] != res[k] and warning_level == WarningLevel.STRICT:
                test_warning(location, method, '{}: {} | expected | {}'.format(k, expected_data[k], res[k]))

    return True


def test(svc_port, location, method, token, data, expected_status, expected_data, warning_level=WarningLevel.STRICT):

    __result = {}

    if not test_db_active():
        test_failed('TEST DATABASE NOT ACTIVE', '', '')
        sys.exit(1)

    if not do_test(svc_port, location, method, token, data, expected_status, expected_data, __result, warning_level):
        test_failed(location, method, __result)
        sys.exit(1)

    test_passed(location, method, __result)
    return __result


if __name__ == '__main__':
    import json
    from base_common.importer import import_from_settings
    from base_common.importer import get_installed_apps

    imported_modules = []
    installed_apps = {}

    get_installed_apps(installed_apps)

    app = sys.argv[1]

    svc_port = installed_apps[app]['svc_port']
    import_from_settings(imported_modules, app)

    result = {}

    import base_api.users.user_register

    test(svc_port, base_api.users.user_register.location, 'GET', None,
         {'username': 'user1@test.loc', 'password': '123'}, 404, {'message': 'GET not implemented'})

    test(svc_port, base_api.users.user_register.location, 'POST', None,
         {'username': 'user1@test.loc', 'password': '123'}, 200, {'token': ''}, WarningLevel.STRICT_ON_KEY)

    test(svc_port, base_api.users.user_register.location, 'POST', None,
         {'username': 'user1@test.loc', 'password': '123'}, 400, {'message': amsgs.msgs[amsgs.USERNAME_ALREADY_TAKEN]})

    # LOGIN TESTS
    import base_api.users.user_login

    tk = test(svc_port, base_api.users.user_login.location, 'POST', None,
              {'username': 'user1@test.loc', 'password': '123'}, 200, {'token': ''},
              warning_level=WarningLevel.STRICT_ON_KEY)['token']
    test(svc_port, base_api.users.user_login.location, 'POST', None,
         {'username': 'no_user@test.loc', 'password': '123'}, 400, {'message': amsgs.msgs[amsgs.USER_NOT_FOUND]})
    test(svc_port, base_api.users.user_login.location, 'POST', None, {'userna': 'no_user@test.loc', 'password': '123'},
         400, {'message': amsgs.msgs[amsgs.MISSING_REQUEST_ARGUMENT]})
    test(svc_port, base_api.users.user_login.location, 'POST', None, {'username': 'no_user@test.loc', 'passwo': '123'},
         400, {'message': amsgs.msgs[amsgs.MISSING_REQUEST_ARGUMENT]})

    # LOGOUT TESTS
    import base_api.users.user_logout

    test(svc_port, base_api.users.user_logout.location, 'POST', None, {}, 400,
         {'message': amsgs.msgs[amsgs.UNAUTHORIZED_REQUEST]})
    test(svc_port, base_api.users.user_logout.location, 'POST', tk, {}, 204, {})

    # FORGOT PASSWORD TESTS
    import base_api.users.forgot_password

    test(svc_port, base_api.users.forgot_password.location, 'POST', None, {'ername': 'user2@test.loc'}, 404,
         {'message': 'POST not implemented'})
    test(svc_port, base_api.users.forgot_password.location, 'PUT', None, {'ername': 'user2@test.loc'}, 400,
         {'message': amsgs.msgs[amsgs.MISSING_REQUEST_ARGUMENT]})
    test(svc_port, base_api.users.forgot_password.location, 'PUT', None, {'username': 'user2@test.loc'}, 400,
         {'message': amsgs.msgs[amsgs.USER_NOT_FOUND]})
    test(svc_port, base_api.users.forgot_password.location, 'PUT', None, {'username': 'user1@test.loc'}, 200, {})

    # HASHING PARAMETERS TESTS
    import base_api.hash2params.save_hash

    test(svc_port, base_api.hash2params.save_hash.location, 'POST', None,
         {'username': 'user2@test.loc', 'password': '123'}, 404, {'message': 'POST not implemented'})
    test(svc_port, base_api.hash2params.save_hash.location, 'PUT', None, {'dat': 'user2@test.loc'}, 400,
         {'message': amsgs.msgs[amsgs.MISSING_REQUEST_ARGUMENT]})
    htk = test(svc_port, base_api.hash2params.save_hash.location, 'PUT', None,
               {'data': json.dumps({"username": "user2@test.loc"})}, 200, {})['h']

    # CHANGE PASSWORD TESTS
    import base_api.users.change_password

    tk = test(svc_port, base_api.users.user_login.location, 'POST', None,
              {'username': 'user1@test.loc', 'password': '123'}, 200, {'token': ''},
              warning_level=WarningLevel.STRICT_ON_KEY)['token']

    test(svc_port, base_api.users.change_password.location, 'POST', None, {'ername': 'user2@test.loc'}, 400,
         {'message': amsgs.msgs[amsgs.MISSING_REQUEST_ARGUMENT]})
    test(svc_port, base_api.users.change_password.location, 'POST', tk, {'newpassword': '123'}, 400,
         {'message': amsgs.msgs[amsgs.MISSING_REQUEST_ARGUMENT]})
    test(svc_port, base_api.users.change_password.location, 'POST', tk, {'newpassword': '123', 'oldpassword': '123'},
         200, {'message': amsgs.msgs[amsgs.USER_PASSWORD_CHANGED]})

    loc = base_api.users.change_password.location[:-2] + '/' + htk
    test(svc_port, loc, 'POST', None, {'newpassword':'123'}, 200, {'message': ''}, result)

    # CHECK USER TESTS
    import base_api.users.user_check

    test(svc_port, base_api.users.user_check.location, 'POST', None, {'username': 'user2@test.loc', 'password': '123'},
         400, {'message': amsgs.msgs[amsgs.UNAUTHORIZED_REQUEST]})
    test(svc_port, base_api.users.user_check.location, 'POST', tk, {'username': 'user2@test.loc', 'password': '123'},
         200, {'username': ''}, warning_level=WarningLevel.STRICT_ON_KEY)
