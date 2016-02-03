import os
import sys
import json

pth = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(pth)

from base_svc.comm import call


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
    NO_WARNING = 0
    STRICT = 1  # DEFAULT
    STRICT_ON_KEY = 2  # ONLY KEY HAS TO BE CHECKED


def test_warning(loc, method, result):
    print(Color.BOLD_YELLOW, 'WARNING', loc, method, '-> {}'.format(result) if result else '', Color.DEFAULT)


def test_failed(loc, method, result):
    print(Color.BOLD_RED, 'FAILED', loc, method, '->', result, Color.DEFAULT)


def test_passed(loc, method, result):
    print(Color.BOLD_GREEN, 'PASSED', loc, method, '-> {}'.format(result) if result else '', Color.DEFAULT)


def test_db_is_active():
    return True


def do_test(svc_port, location, method, token, data, expected_status, expected_data, result, warning_level):
    _headers = None
    if token:
        _headers = {'Authorization': token}

    res, status = call('localhost', svc_port, location, data, method, call_headers=_headers)
    res = json.loads(res) if res else {}
    res.update({'status': status})
    result.update(res)

    if status != expected_status:
        return False

    if expected_data:
        for k in expected_data:

            if k not in res and warning_level != WarningLevel.NO_WARNING:
                return False

            if expected_data[k] != res[k] and warning_level == WarningLevel.STRICT:
                test_warning(location, method, '{}: {} | expected | {}'.format(k, expected_data[k], res[k]))

    return True


def test(svc_port, location, method, token, data, expected_status, expected_data, warning_level=WarningLevel.STRICT):

    __result = {}

    if not test_db_is_active():
        test_failed('TEST DATABASE NOT ACTIVE', '', '')
        sys.exit(1)

    if not do_test(svc_port, location, method, token, data, expected_status, expected_data, __result, warning_level):
        test_failed(location, method, __result)
        sys.exit(1)

    test_passed(location, method, __result)
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

    _db = base_common.dbacommon.get_md2db()
    print('TEST PROSHO')

    # test if test.sql exists
    # test db connection


def finish_test_with_error():
    print(Color.BOLD_RED, 'ERROR TESTING', Color.DEFAULT)
    sys.exit(4)


def finish_tests():

    import tornado.ioloop
    print(Color.BOLD_GREEN, 'FINISH TESTING', Color.DEFAULT)
    tornado.ioloop.IOLoop.instance().stop()
    #sys.exit()
