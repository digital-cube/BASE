# coding: utf-8

import unittest
# import tornado.testing
# from unittest import TestSuite

from base.tests.api.user.test_user_login import TestUserLogin
from base.tests.api.user.test_user_register import TestUserRegister
from base.tests.api.user.test_user_logout import TestUserLogout
from base.tests.api.utils.test_options import TestOptions
from base.tests.api.utils.test_hash_2_params import TestHash2Params
from tests.hello import TestHello


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

