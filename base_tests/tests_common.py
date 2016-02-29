import os
import sys
import json
import logging
from logging.handlers import RotatingFileHandler

pth = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(pth)


from base_svc.comm import call
from base_config.settings import LOG_DIR


log_filename = "{}/tests.log".format(LOG_DIR)
log_handler = RotatingFileHandler(log_filename, maxBytes=1048576, backupCount=2)
log_formatter = logging.Formatter(
        '%(asctime)-6s  - %(message)s')
log_handler.setFormatter(log_formatter)

log = logging.getLogger('DGTT')
log.propagate = False
log.addHandler(log_handler)
log.setLevel(logging.DEBUG)


class Color:
    BLUE = '\033[0;34m'
    BOLD_BLUE = '\033[1;34m'
    GREEN = '\033[0;92m'
    BOLD_GREEN = '\033[1;92m'
    RED = '\033[0;31m'
    BOLD_RED = '\033[1;31m'
    YELLOW = '\033[0;93m'
    BOLD_YELLOW = '\033[1;93m'
    DEFAULT = '\033[0m'


class WarningLevel:
    NO_WARNING = 0  # WITHOUT WARNINGS
    STRICT = 1  # DEFAULT
    STRICT_ON_KEY = 2  # ONLY KEY HAS TO BE CHECKED


def test_log(loc, method, result, color, message):
    st = '{}{} {} {}{}{}'.format(color, message, loc, method, '-> {}'.format(result) if result else '', Color.DEFAULT)
    try:
        log.info(st)
    except Exception as e:
        log.critical(e)


def log_info(loc, method, result):
    test_log(loc, method, result, Color.BLUE, 'INFO')


def log_warning(loc, method, result):
    test_log(loc, method, result, Color.BOLD_YELLOW, 'WARNING')


def log_failed(loc, method, result):
    test_log(loc, method, result, Color.BOLD_RED, 'FAILED')


def log_passed(loc, method, result):
    test_log(loc, method, result, Color.BOLD_GREEN, 'PASSED')


def test_db_is_active():
    return True


def do_test(svc_port, location, method, token, data, expected_status, expected_data, result, result_types, warning_level):
    _headers = None
    if token:
        _headers = {'Authorization': token}

    res, status = call('localhost', svc_port, location, data, method, call_headers=_headers)

    try:
        res = json.loads(res) if res else {}
    except Exception as e:
        log_warning('Error load json data: {}'.format(res), '', None)
        log_warning('Error: {}'.format(e), '', None)
        result.update({'message': res})
        res = {'message': res}

    res.update({'status': status})
    result.update(res)

    if status != expected_status:
        return False

    if result_types and not expected_data:
        log_warning('Missing expected data for given result_types: {}'.format(result_types), '', None)
        return False

    if expected_data:
        # inspect expected results
        for k in expected_data:

            if k not in res and warning_level != WarningLevel.NO_WARNING:
                return False

            if expected_data[k] != res[k] and warning_level == WarningLevel.STRICT:
                log_warning(location, method, '{}: {} | expected | {}'.format(k, res[k], expected_data[k]))

        # inspect result types
        if result_types:
            if not set(result_types.keys()).issubset(set(expected_data.keys())):
                log_warning('Expected results and results types differ', '', None)
                return False

            for k in result_types:

                if k not in res:
                    log_warning('Missing result {}'.format(k), '', None)
                    return False

                if type(res[k]) != result_types[k]:
                    log_warning('Result types for {} differ: got {} expected {}'.format(k, type(res[k]), result_types[k]), '', None)
                    return False

    return True


def test(svc_port, location, method, token, data, expected_status, expected_data, result_types={}, warning_level=WarningLevel.STRICT):

    __result = {}

    if not test_db_is_active():
        log_failed('TEST DATABASE NOT ACTIVE', '', '')
        sys.exit(1)

    if not do_test(svc_port, location, method, token, data, expected_status, expected_data, __result, result_types, warning_level):
        log_failed(location, method, __result)
        sys.exit(1)

    log_passed(location, method, __result)
    return __result


def prepare_test_env():

    from collections import namedtuple
    import base_config.settings
    import base_common.dbacommon

    db_name = 'test_{}'.format(base_config.settings.APP_DB.db)
    dbtest = namedtuple('DbTest', 'db, host, user, passwd, charset')
    db_test = dbtest(
        db_name,
        'localhost',
        base_config.settings.APP_DB.user,
        base_config.settings.APP_DB.passwd,
        'utf8')
    base_config.settings.APP_DB = db_test

    _db = base_common.dbacommon.get_db()

    # test if test.sql exists
    # test db connection


def finish_test_with_error():
    st = '{}{}{}'.format(Color.BOLD_RED, 'ERROR TESTING', Color.DEFAULT)
    log.info(st)
    print(st)
    import tornado.ioloop
    tornado.ioloop.IOLoop.instance().stop()
    sys.exit(4)


def finish_tests():

    st = '{}{}{}'.format(Color.BOLD_GREEN, 'FINISH TESTING', Color.DEFAULT)
    log.info(st)
    print(st)
    import tornado.ioloop
    tornado.ioloop.IOLoop.instance().stop()
    sys.exit()


def load_app_test(app_started, app_tests_list, stage):

    from base_common.importer import import_from_settings
    from base_common.importer import get_installed_apps
    from base_common.importer import get_app
    import base_tests.test_list
    imported_modules = []
    installed_apps = {}
    get_installed_apps(installed_apps)
    import_from_settings(imported_modules, app_started)

    _installed_app = get_app()
    _pm = _installed_app['pkg']
    import importlib
    app_tests = importlib.import_module(_pm.TESTS)

    for itest in app_tests.tests_included:

        t_s = itest[1]
        if t_s < stage:
            continue

        t_n = itest[0]
        app_test = getattr(app_tests, t_n)

        if hasattr(base_tests.test_list, t_n):
            log_info('OVERLOADING {}'.format(t_n), '', None)
            setattr(base_tests.test_list, t_n, app_test)

        else:
            log_info('LOADING {}'.format(t_n), '', None)
            app_tests_list.append((app_test, t_s))


