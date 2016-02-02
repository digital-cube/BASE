import os
import sys

pth = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(pth)

from base_config.settings import TEST_PORT

from base_tests.test_list import user_register_test
from base_tests.test_list import user_login_test
from base_tests.test_list import user_logout_test
from base_tests.test_list import user_forgot_password_test
from base_tests.test_list import hash_save_test
from base_tests.test_list import hash_retrieve_test
from base_tests.test_list import user_change_password_test
from base_tests.test_list import user_check_test
from base_tests.tests_common import finish_tests


def test_base(svc_port):

    # USER REGISTER TEST
    user_register_test(svc_port)

    # LOGIN TESTS
    user_login_test(svc_port)

    # LOGOUT TESTS
    user_logout_test(svc_port)

    # FORGOT PASSWORD TESTS
    user_forgot_password_test(svc_port)

    # HASHI SAVE TESTS
    hash_save_test(svc_port)

    # HASHI RETRIEVE TESTS
    hash_retrieve_test(svc_port)

    # CHANGE PASSWORD TESTS
    user_change_password_test(svc_port)

    # CHECK USER TESTS
    user_check_test(svc_port)


def run_tests():

    import time
    time.sleep(3)

    svc_port = TEST_PORT

    test_base(svc_port)

    finish_tests()

if __name__ == '__main__':

    run_tests()


