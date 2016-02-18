
tests_included = [
    'echo_get_test',
    'echo_put_test',
    'echo_delete_test',
    'echo_post_test',
    'echo_patch_test',
]

prefix = 'api'

import base_lookup.api_messages as amsgs
from base_tests.tests_common import test, WarningLevel, log_info


def echo_get_test(svc_port):
    log_info("Echo Get test", '', None)

    import echo
    loc = '{}/{}'.format(prefix, echo.location)

    test(svc_port, loc, 'GET', None, {}, 400, {'message': amsgs.msgs[amsgs.MISSING_REQUEST_ARGUMENT]})
    test(svc_port, loc, 'GET', None, {'message': 'Test message'}, 200, {'echo': 'Test message'})
    test(svc_port, loc, 'GET', None, {'message': 'Test message'}, 200, {'echo': 'Test message'})
    test(svc_port, loc, 'GET', None, {'message': 'Test message'}, 200, {'echo': 'Test message'},
         result_types={'echo': str})
    test(svc_port, loc, 'GET', None, {'message': 'Test message'}, 200, {'echo': 'Test'}, result_types={'echo': str},
         warning_level=WarningLevel.STRICT_ON_KEY)


def echo_put_test(svc_port):
    log_info("Echo Put test", '', None)

    import echo
    loc = '{}/{}'.format(prefix, echo.location)

    test(svc_port, loc, 'PUT', None, {}, 400, {'message': amsgs.msgs[amsgs.MISSING_REQUEST_ARGUMENT]})
    test(svc_port, loc, 'PUT', None, {'message': 'Test message'}, 400,
         {'message': amsgs.msgs[amsgs.INVALID_REQUEST_ARGUMENT]})
    test(svc_port, loc, 'PUT', None, {'message': '00-22'}, 400, {'message': amsgs.msgs[amsgs.INVALID_REQUEST_ARGUMENT]})
    test(svc_port, loc, 'PUT', None, {'message': '2016-10-12 22:22:22'}, 400,
         {'message': amsgs.msgs[amsgs.INVALID_REQUEST_ARGUMENT]})
    test(svc_port, loc, 'PUT', None, {'message': '2016-10-12'}, 200, {'echo': '2016-10-12'}, result_types={'echo': str})
    test(svc_port, loc, 'PUT', None, {'message': '2016-10-12'}, 200, {'echo': 'Test'}, result_types={'echo': str},
         warning_level=WarningLevel.STRICT_ON_KEY)


def echo_delete_test(svc_port):
    log_info("Echo Delete test", '', None)

    import echo
    loc = '{}/{}'.format(prefix, echo.location)

    test(svc_port, loc, 'DELETE', None, {}, 400, {'message': amsgs.msgs[amsgs.MISSING_REQUEST_ARGUMENT]})
    test(svc_port, loc, 'DELETE', None, {'message': 'Test message'}, 400,
         {'message': amsgs.msgs[amsgs.INVALID_REQUEST_ARGUMENT]})
    test(svc_port, loc, 'DELETE', None, {'message': '00-22'}, 400,
         {'message': amsgs.msgs[amsgs.INVALID_REQUEST_ARGUMENT]})
    test(svc_port, loc, 'DELETE', None, {'message': '2016-10-12'}, 400,
         {'message': amsgs.msgs[amsgs.INVALID_REQUEST_ARGUMENT]})
    test(svc_port, loc, 'DELETE', None, {'message': '2016-10-12 22:22:22'}, 200, {'echo': '2016-10-12 22:22:22'},
         result_types={'echo': str})
    test(svc_port, loc, 'DELETE', None, {'message': '2016-10-12 22:22:22'}, 200, {'echo': 'Test'},
         result_types={'echo': str}, warning_level=WarningLevel.STRICT_ON_KEY)


def echo_post_test(svc_port):
    log_info("Echo Post test", '', None)

    import echo
    loc = '{}/{}'.format(prefix, echo.location)

    test(svc_port, loc, 'POST', None, {}, 400, {'message': amsgs.msgs[amsgs.MISSING_REQUEST_ARGUMENT]})
    test(svc_port, loc, 'POST', None, {'message': 'Test message'}, 400,
         {'message': amsgs.msgs[amsgs.INVALID_REQUEST_ARGUMENT]})
    test(svc_port, loc, 'POST', None, {'message': '00-22'}, 400,
         {'message': amsgs.msgs[amsgs.INVALID_REQUEST_ARGUMENT]})
    test(svc_port, loc, 'POST', None, {'message': '2016-10-12'}, 400,
         {'message': amsgs.msgs[amsgs.INVALID_REQUEST_ARGUMENT]})
    test(svc_port, loc, 'POST', None, {'message': '{"1":1, "2":2}'}, 200, {'echo': '{"1":1, "2":2}'},
         result_types={'echo': str}, warning_level=WarningLevel.STRICT_ON_KEY)


def echo_patch_test(svc_port):
    log_info("Echo Post test", '', None)

    import echo
    loc = '{}/{}'.format(prefix, echo.location)

    test(svc_port, loc, 'PATCH', None, {}, 400, {'message': amsgs.msgs[amsgs.MISSING_REQUEST_ARGUMENT]})
    test(svc_port, loc, 'PATCH', None, {'message': 'Test message'}, 400,
         {'message': amsgs.msgs[amsgs.INVALID_REQUEST_ARGUMENT]})
    test(svc_port, loc, 'PATCH', None, {'message': '00-22'}, 400,
         {'message': amsgs.msgs[amsgs.INVALID_REQUEST_ARGUMENT]})
    test(svc_port, loc, 'PATCH', None, {'message': 1}, 200, {'echo': 1}, result_types={'echo': int})
    test(svc_port, loc, 'PATCH', None, {'message': '1'}, 200, {'echo': 1}, result_types={'echo': int})
    test(svc_port, loc, 'PATCH', None, {'message': 1}, 200, {'echo': '1'},
         result_types={'echo': int}, warning_level=WarningLevel.STRICT_ON_KEY)
