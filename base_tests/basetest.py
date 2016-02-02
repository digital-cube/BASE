import os
import sys

pth = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(pth)

from base_tests.test_list import user_register_test
from base_tests.test_list import user_login_test
from base_tests.test_list import user_logout_test
from base_tests.test_list import user_forgot_password_test
from base_tests.test_list import hash_save_test
from base_tests.test_list import hash_retrieve_test
from base_tests.test_list import user_change_password_test
from base_tests.test_list import user_check_test


if __name__ == '__main__':

    svc_port = 8801

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
