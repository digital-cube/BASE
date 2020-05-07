# coding: utf-8

import os
import sys
import unittest
import tornado.testing
from unittest import TestSuite

# from base.tests.api.user.test_user_change_password import TestUserChangePassword
# from base.tests.api.user.test_user_forgot_password import TestUserForgot
# from base.tests.api.user.test_user_login import TestUserLogin
# from base.tests.api.user.test_user_logout import TestUserLogout
# from base.tests.api.user.test_user_register import TestUserRegister
# from base.tests.api.user.test_user_g_access import TestUserGAccess
# from base.tests.api.user.test_user_f_access import TestUserFAccess
# from base.tests.api.utils.test_hash_2_params import TestHash2Params
# from base.tests.api.utils.test_mail_queue import TestMailQueue
# from base.tests.api.utils.test_mail_queue import TestMailQueueSetOptions
# from base.tests.api.utils.test_mail_queue import TestMailQueueGet
# from base.tests.api.utils.test_options import TestOptions


_root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
sys.path.append(_root_dir)

from tests.test_hello import TestHello, TestHelloWorld

def all():
    # _tests = [TestUserChangePassword, TestUserForgot, TestUserLogin, TestUserLogout, TestUserRegister, TestUserGAccess, TestUserFAccess, TestHash2Params, TestMailQueue, TestMailQueueSetOptions, TestMailQueueGet, TestOptions, TestHello, TestHelloWorld]
    _tests = [TestHello, TestHelloWorld]

    _loader = unittest.TestLoader()
    _tests = [_loader.loadTestsFromTestCase(t) for t in _tests]
    _all = TestSuite(_tests)
    return _all
    

if __name__ == '__main__':
    """
    Run all tests in a suite.
    """

    tornado.testing.main()

