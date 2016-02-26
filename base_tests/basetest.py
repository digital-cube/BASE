import os
import sys
import time

pth = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(pth)

import base_config.settings

import base_tests.test_list
from base_tests.tests_common import finish_tests
from base_tests.tests_common import load_app_test
from base_tests.tests_common import log_failed
import base_tests.tests_common


def test_base(svc_port):

    if not base_config.settings.BASE_TEST:
        return

    try:
        # USER REGISTER TEST
        base_tests.test_list.base_user_register_test(svc_port)

        # LOGIN TESTS
        base_tests.test_list.base_user_login_test(svc_port)

        # LOGOUT TESTS
        base_tests.test_list.base_user_logout_test(svc_port)

        # FORGOT PASSWORD TESTS
        base_tests.test_list.base_user_forgot_password_test(svc_port)

        # HASHI SAVE TESTS
        base_tests.test_list.base_hash_save_test(svc_port)

        # HASH RETRIEVE TESTS
        base_tests.test_list.base_hash_retrieve_test(svc_port)

        # CHANGE PASSWORD TESTS
        base_tests.test_list.base_user_change_password_test(svc_port)

        # CHECK USER TESTS
        base_tests.test_list.base_user_check_test(svc_port)

        # CHANGE USERNAME TEST
        base_tests.test_list.base_user_change_username_test(svc_port)

        # CHANGING USERNAME TEST
        base_tests.test_list.base_user_changing_username_test(svc_port)

        # SAVE MAIL TEST
        base_tests.test_list.base_save_message_test(svc_port)
    except Exception as e:
        log_failed('Error in test: {}'.format(e), '', None)
        sys.exit(1)


def _prepare_stage_dump(_test_db, db_user, db_passwd, stage):

    import os

    dbm_file_dir_path = os.path.abspath(os.path.join(os.path.abspath(__file__), '../../..'))
    dbm_file_path = os.path.abspath(os.path.join(dbm_file_dir_path, '{}_stage_{}_.dmp'.format(_test_db, stage)))

    dump_app = 'mysqldump'

    #todo make dump __proj__.stage[last_stage].dump
    dump_cmd = '{} -u{} -p{} {} > {}'.format(
        dump_app, db_user, db_passwd, _test_db, dbm_file_path
    )

    os.system(dump_cmd)


def test_app(app_tests_list, svc_port, t_stage, t_db, db_u, db_p):

    last_stage = t_stage
    if app_tests_list:

        for itest in app_tests_list:

            current_stage = itest[1]

            if last_stage<current_stage:
                _prepare_stage_dump(t_db, db_u, db_p, last_stage)
                #todo make dump __proj__.stage[last_stage].dump

            try:
                itest[0](svc_port)
            except Exception as e:
                log_failed('Error in test: {}'.format(e), '', None)
                sys.exit(1)

            last_stage = current_stage


def run_tests(app_started, t_stage, test_db, db_user, db_passwd):

    time.sleep(1) # TODO: pingovati service da li je ok da nastavish

    svc_port = base_config.settings.TEST_PORT

    app_tests_list = []
    load_app_test(app_started, app_tests_list, t_stage)

    test_base(svc_port)
    test_app(app_tests_list, svc_port, t_stage, test_db, db_user, db_passwd)

    finish_tests()


def prepare_test_db(_test_db, user, passwd, t_stage):
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

    if t_stage != 0:
        dbm_file_path = os.path.abspath(os.path.join(dbm_file_dir_path, '{}_stage_{}_.dmp'.format(_test_db, t_stage-1)))

    fill_test_db_cmd = "{} -u{} -p{} {} < {}".format(
        db_app, db_user, passwd, _test_db, dbm_file_path
    )

    # create test db tables
    os.system(fill_test_db_cmd)

    if t_stage == 0:
        os.unlink(dbm_file_path)


if __name__ == '__main__':

    app_started = sys.argv[1]
    test_db = sys.argv[2]
    db_user = sys.argv[3]
    db_passwd = sys.argv[4]
    t_stage = int(sys.argv[5]) if len(sys.argv) == 6 else 0

    prepare_test_db(test_db, db_user, db_passwd, t_stage)
    run_tests(app_started, t_stage, test_db, db_user, db_passwd)


