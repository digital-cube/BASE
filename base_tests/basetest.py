# -*- coding: utf-8 -*-

import os
import sys
import time

pth = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(pth)

import base_config.settings

import base_tests.test_list
from base_tests.tests_common import finish_tests
from base_tests.tests_common import load_app_test
from base_tests.tests_common import log_failed, log_info
import base_tests.tests_common


def test_base(svc_port, t_stage):

    if not base_config.settings.BASE_TEST or t_stage != 0:
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

        # SET OPTIONS TEST
        base_tests.test_list.base_set_option_test(svc_port)

        # GET OPTIONS TEST
        base_tests.test_list.base_get_option_test(svc_port)

        # DELETE OPTIONS TEST
        base_tests.test_list.base_del_option_test(svc_port)

        # SHOW API SPECIFICATION TEST
        base_tests.test_list.show_api_spec_test(svc_port)

    except Exception as e:
        log_failed('Error in test: {}'.format(e), '', None)
        import tornado.ioloop
        tornado.ioloop.IOLoop.instance().stop()
        sys.exit(1)


def _prepare_stage_dump(_test_db, db_user, db_passwd, stage):

    import os

    dbm_file_dir_path = os.path.abspath(os.path.join(os.path.abspath(__file__), '../../..'))
    dbm_file_path = os.path.abspath(os.path.join(dbm_file_dir_path, '{}_stage_{}_.dmp'.format(_test_db, stage)))

    dump_app = 'mysqldump'

    dump_cmd = '{} -u{} -p{} {} > {}'.format(
        dump_app, db_user, db_passwd, _test_db, dbm_file_path
    )

    os.system(dump_cmd)


def test_app(app_tests_list, svc_port, t_stage, t_db, db_u, db_p):

    last_stage = t_stage
    if app_tests_list:

        for itest in app_tests_list:

            log_info('','Executing test {}'.format(itest),'')


            current_stage = itest[1]

            if last_stage < current_stage:
                _prepare_stage_dump(t_db, db_u, db_p, last_stage)

            try:
                itest[0](svc_port)
            except Exception as e:
                log_failed('Error in test: {}'.format(e), '', None)
                import tornado.ioloop
                tornado.ioloop.IOLoop.instance().stop()
                sys.exit(1)

            last_stage = current_stage


def run_tests(app_started, t_stage, test_db, db_user, db_passwd, server_pid):

    time.sleep(1) # TODO: pingovati service da li je ok da nastavish

    svc_port = base_config.settings.TEST_PORT

    app_tests_list = []
    load_app_test(app_started, app_tests_list, t_stage)

    test_base(svc_port, t_stage)
    test_app(app_tests_list, svc_port, t_stage, test_db, db_user, db_passwd)

    finish_tests(server_pid)


def add_keep_tables(required_tables, tables_to_keep):

    if t_keep:
        required_tables += ' '
        required_tables += ' '.join(tables_to_keep.split(','))

    return required_tables


def prepare_test_db(_test_db, user, passwd, t_stage, t_keep):
    t = len('test_')
    db_name = _test_db[t:]

    import os

    dbm_file_dir_path = os.path.abspath(os.path.join(os.path.abspath(__file__), '../../..'))
    dbm_file_path = os.path.abspath(os.path.join(dbm_file_dir_path, '{}.dmp'.format(_test_db)))

    db_app = 'mysql'
    dump_app = 'mysqldump'
    required_tables = 'sequencers'
    required_tables = add_keep_tables(required_tables, t_keep)

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
    t_stage = 0
    t_keep = ''
    s_pid = 0

    for _a in sys.argv:
        _a_idx = sys.argv.index(_a)
        if _a == '-s':
            t_stage = int(sys.argv[_a_idx + 1])

        if _a == '-k':
            t_keep = sys.argv[_a_idx + 1]

        if _a == '-p':
            s_pid = int(sys.argv[_a_idx + 1])
            setattr(base_config.settings, 'S_PID', s_pid)

    prepare_test_db(test_db, db_user, db_passwd, t_stage, t_keep)
    run_tests(app_started, t_stage, test_db, db_user, db_passwd, s_pid)


