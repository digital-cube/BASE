# coding: utf-8

import os
import sys
import unittest
# import tornado.testing
# from unittest import TestSuite

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

_current_dir = os.getcwd()
_current_dir_from_file = os.path.dirname(os.path.abspath(__file__))
_parent_dir = '/'.join(_current_dir_from_file.split('/')[:-1])
if _parent_dir != _current_dir:
    os.chdir(_parent_dir)
sys.path.append(os.path.abspath(_parent_dir))

try:
    from hello import TestHello, TestHelloWorld
except ImportError:
    from tests.hello import TestHello, TestHelloWorld


# def all():
#     _all = TestSuite()
#     _all.addTest(TestUserRegister('test_register'))
#     _all.addTest(TestUserRegister('test_register_with_same_username'))
#     return _all

if __name__ == '__main__':
    """
    Run all tests.
    Make sure the test database is created. For postgresql and mysql create database test_[configured database name]
    """

    unittest.main()
    # all()
    # tornado.testing.main()

