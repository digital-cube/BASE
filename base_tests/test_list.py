import os
import sys
import json

pth = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(pth)

import base_lookup.api_messages as amsgs
from base_tests.tests_common import WarningLevel, test
from base_tests.tests_common import log


def user_register_test(svc_port):

    import base_api.users.user_register

    test(svc_port, base_api.users.user_register.location, 'GET', None,
         {'username': 'user1@test.loc', 'password': '123'}, 404, {'message': amsgs.msgs[amsgs.NOT_IMPLEMENTED_GET]})

    test(svc_port, base_api.users.user_register.location, 'POST', None,
         {'username': 'user1@test.loc', 'password': '123'}, 200, {'token': ''}, result_types={'token': str},
         warning_level=WarningLevel.STRICT_ON_KEY)

    test(svc_port, base_api.users.user_register.location, 'POST', None,
         {'username': 'user1@test.loc', 'password': '123'}, 400, {'message': amsgs.msgs[amsgs.USERNAME_ALREADY_TAKEN]})


def user_login_test(svc_port):

    import base_api.users.user_login

    test(svc_port, base_api.users.user_login.location, 'POST', None, {'username': 'user1@test.loc', 'password': '123'},
         200, {'token': ''}, result_types={'token': str}, warning_level=WarningLevel.STRICT_ON_KEY)
    test(svc_port, base_api.users.user_login.location, 'POST', None,
         {'username': 'no_user@test.loc', 'password': '123'}, 400, {'message': amsgs.msgs[amsgs.USER_NOT_FOUND]})
    test(svc_port, base_api.users.user_login.location, 'POST', None, {'userna': 'no_user@test.loc', 'password': '123'},
         400, {'message': amsgs.msgs[amsgs.MISSING_REQUEST_ARGUMENT]})
    test(svc_port, base_api.users.user_login.location, 'POST', None, {'username': 'no_user@test.loc', 'passwo': '123'},
         400, {'message': amsgs.msgs[amsgs.MISSING_REQUEST_ARGUMENT]})


def user_logout_test(svc_port):

    import base_api.users.user_login
    import base_api.users.user_logout

    tk = test(svc_port, base_api.users.user_login.location, 'POST', None,
              {'username': 'user1@test.loc', 'password': '123'}, 200, {'token': ''}, result_types={'token': str},
              warning_level=WarningLevel.STRICT_ON_KEY)['token']

    test(svc_port, base_api.users.user_logout.location, 'POST', None, {}, 400,
         {'message': amsgs.msgs[amsgs.UNAUTHORIZED_REQUEST]})
    test(svc_port, base_api.users.user_logout.location, 'POST', tk, {}, 204, {})


def user_forgot_password_test(svc_port):

    import base_api.users.forgot_password

    test(svc_port, base_api.users.forgot_password.location, 'POST', None, {'ername': 'user2@test.loc'}, 404,
         {'message': amsgs.msgs[amsgs.NOT_IMPLEMENTED_POST]})
    test(svc_port, base_api.users.forgot_password.location, 'PUT', None, {'ername': 'user2@test.loc'}, 400,
         {'message': amsgs.msgs[amsgs.MISSING_REQUEST_ARGUMENT]})
    test(svc_port, base_api.users.forgot_password.location, 'PUT', None, {'username': 'user2@test.loc'}, 400,
         {'message': amsgs.msgs[amsgs.USER_NOT_FOUND]})
    test(svc_port, base_api.users.forgot_password.location, 'PUT', None, {'username': 'user1@test.loc'}, 200, {})


def user_change_password_test(svc_port):

    import base_api.users.user_login
    import base_api.hash2params.save_hash
    import base_api.users.change_password

    tk = test(svc_port, base_api.users.user_login.location, 'POST', None,
              {'username': 'user1@test.loc', 'password': '123'}, 200, {'token': ''}, result_types={'token': str},
              warning_level=WarningLevel.STRICT_ON_KEY)['token']
    htk = test(svc_port, base_api.hash2params.save_hash.location, 'PUT', None,
               {'data': json.dumps({"username": "user2@test.loc"})}, 200, {})['h']

    test(svc_port, base_api.users.change_password.location, 'POST', None, {'ername': 'user2@test.loc'}, 400,
         {'message': amsgs.msgs[amsgs.MISSING_REQUEST_ARGUMENT]})
    test(svc_port, base_api.users.change_password.location, 'POST', tk, {'newpassword': '123'}, 400,
         {'message': amsgs.msgs[amsgs.MISSING_REQUEST_ARGUMENT]})
    test(svc_port, base_api.users.change_password.location, 'POST', tk, {'newpassword': '123', 'oldpassword': '123'},
         200, {'message': amsgs.msgs[amsgs.USER_PASSWORD_CHANGED]}, result_types={'message': str})

    loc = base_api.users.change_password.location[:-2] + '/' + htk
    test(svc_port, loc, 'POST', None, {'newpassword': '123'}, 200, {'message': ''}, result_types={'message': str},
         warning_level=WarningLevel.STRICT_ON_KEY)


def user_check_test(svc_port):

    import base_api.users.user_login
    import base_api.users.user_check

    tk = test(svc_port, base_api.users.user_login.location, 'POST', None,
              {'username': 'user1@test.loc', 'password': '123'}, 200, {'token': ''}, result_types={'token': str},
              warning_level=WarningLevel.STRICT_ON_KEY)['token']

    test(svc_port, base_api.users.user_check.location, 'POST', None, {'username': 'user2@test.loc', 'password': '123'},
         400, {'message': amsgs.msgs[amsgs.UNAUTHORIZED_REQUEST]})
    test(svc_port, base_api.users.user_check.location, 'POST', tk, {'username': 'user2@test.loc', 'password': '123'},
         200, {'username': ''}, result_types={'username': str}, warning_level=WarningLevel.STRICT_ON_KEY)


def hash_save_test(svc_port):

    import base_api.hash2params.save_hash

    test(svc_port, base_api.hash2params.save_hash.location, 'POST', None,
         {'username': 'user2@test.loc', 'password': '123'}, 404, {'message': amsgs.msgs[amsgs.NOT_IMPLEMENTED_POST]})
    test(svc_port, base_api.hash2params.save_hash.location, 'PUT', None, {'dat': 'user2@test.loc'}, 400,
         {'message': amsgs.msgs[amsgs.MISSING_REQUEST_ARGUMENT]})
    test(svc_port, base_api.hash2params.save_hash.location, 'PUT', None,
         {'data': json.dumps({"username": "user2@test.loc"})}, 200, {})


def hash_retrieve_test(svc_port):

    import base_api.hash2params.save_hash
    import base_api.hash2params.retrieve_hash

    htk = test(svc_port, base_api.hash2params.save_hash.location, 'PUT', None,
               {'data': json.dumps({"username": "user2@test.loc"})}, 200, {})['h']

    test(svc_port, base_api.hash2params.retrieve_hash.location, 'PUT', None, {'hash': htk}, 404,
         {'message': amsgs.msgs[amsgs.NOT_IMPLEMENTED_PUT]})
    test(svc_port, base_api.hash2params.retrieve_hash.location, 'GET', None,
         {'hash': htk[:20]}, 400, {'message': ''}, warning_level=WarningLevel.STRICT_ON_KEY)
    test(svc_port, base_api.hash2params.retrieve_hash.location, 'GET', None,
         {'hash': htk}, 200, {})


def user_change_username_test(svc_port):

    import base_api.users.user_login
    import base_api.users.change_username

    tk = test(svc_port, base_api.users.user_login.location, 'POST', None,
              {'username': 'user1@test.loc', 'password': '123'}, 200, {'token': ''}, result_types={'token': str},
              warning_level=WarningLevel.STRICT_ON_KEY)['token']

    test(svc_port, base_api.users.change_username.location, 'POST', None, {'username': '', 'password': ''},
         400, {'message': amsgs.msgs[amsgs.UNAUTHORIZED_REQUEST]})
    test(svc_port, base_api.users.change_username.location, 'POST', tk, {'username': 'user21@test.loc'}, 400,
         {'message': amsgs.msgs[amsgs.MISSING_REQUEST_ARGUMENT]})
    test(svc_port, base_api.users.change_username.location, 'POST', tk,
         {'username': 'user21@test.loc', 'password': '12'}, 400, {'message': amsgs.msgs[amsgs.WRONG_PASSWORD]})
    test(svc_port, base_api.users.change_username.location, 'POST', tk,
         {'username': 'user21@test.loc', 'password': '123'}, 200,
         {'message': amsgs.msgs[amsgs.CHANGE_USERNAME_REQUEST]}, result_types={'message': str})


def user_changing_username_test(svc_port):

    import base_api.users.user_login
    import base_api.hash2params.save_hash
    import base_api.users.changing_username

    tk = test(svc_port, base_api.users.user_login.location, 'POST', None,
              {'username': 'user1@test.loc', 'password': '123'}, 200, {'token': ''}, result_types={'token': str},
              warning_level=WarningLevel.STRICT_ON_KEY)['token']

    import base_common.dbacommon
    _db = base_common.dbacommon.get_md2db('test_')
    n, p, u_id = base_common.dbatokens.get_user_by_token(_db.cursor(), tk, log)

    hdata = {'cmd': 'change_username', 'newusername': 'user21@test.loc', 'user_id': u_id, 'password': '123'}
    htk = test(svc_port, base_api.hash2params.save_hash.location, 'PUT', None, {'data': json.dumps(hdata)}, 200, {})['h']

    loc = base_api.users.changing_username.location[:-2] + htk
    test(svc_port, loc, 'GET', None, {}, 200, {'message': amsgs.msgs[amsgs.USER_NAME_CHANGED]},
         result_types={'message': str})
    test(svc_port, loc, 'GET', None, {}, 400, {'message': amsgs.msgs[amsgs.PASSWORD_TOKEN_EXPIRED]},
         result_types={'message': str})

    hdata1 = {'cmd': 'change_username', 'newusername': 'user1@test.loc', 'user_id': u_id, 'password': '123'}
    htk1 = test(svc_port, base_api.hash2params.save_hash.location, 'PUT', None, {'data': json.dumps(hdata1)}, 200, {})['h']

    loc1 = base_api.users.changing_username.location[:-2] + htk1
    test(svc_port, loc1, 'GET', None, {}, 200, {'message': amsgs.msgs[amsgs.USER_NAME_CHANGED]},
         result_types={'message': str})


def save_message_test(svc_port):

    # SEND MAIL IS NOT REGISTERED FOR API
    import base_api.mail_api.save_mail

    test(svc_port, base_api.mail_api.save_mail.location, 'POST', None,
         {'username': 'user21@test.loc', 'password': '123'}, 404, {'message': ''},
         warning_level=WarningLevel.STRICT_ON_KEY)
