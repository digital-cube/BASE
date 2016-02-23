import os
import sys
import time

pth = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(pth)

import base_config.settings

import base_tests.test_list
from base_tests.tests_common import finish_tests
from base_tests.tests_common import load_app_test
import base_tests.tests_common


def test_base(svc_port):

    if not base_config.settings.BASE_TEST:
        return

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

    # CHANGE USERNAME TEST
    base_tests.test_list.user_change_username_test(svc_port)

    # CHANGING USERNAME TEST
    base_tests.test_list.user_changing_username_test(svc_port)

    # SAVE MAIL TEST
    base_tests.test_list.save_message_test(svc_port)


def test_app(app_tests_list, svc_port):

    if app_tests_list:

        for itest in app_tests_list:

            itest(svc_port)


def run_tests(app_started):

    time.sleep(1)

    svc_port = base_config.settings.TEST_PORT

    app_tests_list = []
    load_app_test(app_started, app_tests_list)

    test_base(svc_port)
    test_app(app_tests_list, svc_port)

    finish_tests()


def prepare_test_db(_test_db, user, passwd):
    t = len('test_')
    db_name = _test_db[t:]

    import os

    dbm_file_dir_path = os.path.abspath(os.path.join(os.path.abspath(__file__), '../../..'))
    dbm_file_path = os.path.abspath(os.path.join(dbm_file_dir_path, '{}.dmp'.format(_test_db)))

    db_app = 'mysql'
    dump_app = 'mysqldump'
    required_tables = 'sequencers'

    dump_cmd = '{} -u{} -p{} -d {} > {}'.format(
        dump_app, user, passwd, db_name, dbm_file_path
    )
    os.system(dump_cmd)
    dump_required_tables_cmd = '{} -u{} -p{} {} -t {} >> {}'.format(
        dump_app, user, passwd, db_name, required_tables, dbm_file_path
    )
    os.system(dump_required_tables_cmd)

    destroy_test_db_cmd = "{} -u{} -p{} -e 'drop database if exists {}'".format(db_app, user, passwd, _test_db)
    create_test_db_cmd = "{} -u{} -p{} -e 'create database {}'".format(db_app, user, passwd, _test_db)
    # destroy test db if exists
    os.system(destroy_test_db_cmd)
    # create test databse
    os.system(create_test_db_cmd)

    fill_test_db_cmd = "{} -u{} -p{} {} < {}".format(
        db_app, db_user, passwd, _test_db, dbm_file_path
    )

    # create test db tables
    os.system(fill_test_db_cmd)
    os.unlink(dbm_file_path)


if __name__ == '__main__':

    app_started = sys.argv[1]
    test_db = sys.argv[2]
    db_user = sys.argv[3]
    db_passwd = sys.argv[4]

    prepare_test_db(test_db, db_user, db_passwd)
    run_tests(app_started)


