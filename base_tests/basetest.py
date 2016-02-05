import os
import sys
import time

pth = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(pth)

from base_config.settings import TEST_PORT

import base_tests.test_list
from base_tests.tests_common import finish_tests
from base_tests.tests_common import load_app_test
import base_tests.tests_common


def test_base(svc_port):

    # USER REGISTER TEST
    base_tests.test_list.user_register_test(svc_port)

    # LOGIN TESTS
    base_tests.test_list.user_login_test(svc_port)

    # LOGOUT TESTS
    base_tests.test_list.user_logout_test(svc_port)

    # FORGOT PASSWORD TESTS
    base_tests.test_list.user_forgot_password_test(svc_port)

    # HASHI SAVE TESTS
    base_tests.test_list.hash_save_test(svc_port)

    # HASH RETRIEVE TESTS
    base_tests.test_list.hash_retrieve_test(svc_port)

    # CHANGE PASSWORD TESTS
    base_tests.test_list.user_change_password_test(svc_port)

    # CHECK USER TESTS
    base_tests.test_list.user_check_test(svc_port)


def test_app(app_tests_list, svc_port):

    if app_tests_list:

        for itest in app_tests_list:

            itest(svc_port)


def run_tests(app_started):

    time.sleep(3)

    svc_port = TEST_PORT

    app_tests_list = []
    load_app_test(app_started, app_tests_list)

    test_base(svc_port)
    test_app(app_tests_list, svc_port)

    finish_tests()

if __name__ == '__main__':

    app_started = sys.argv[1]
    run_tests(app_started)


