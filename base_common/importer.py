import sys
import importlib
from inspect import getmembers, isfunction
from base_config.settings import APPS, BASE_APPS, TEST_PORT
import base_config.settings
import base_lookup.api_messages
import base_lookup.http_methods as _hm
from base_common.dbaexc import ApplicationNameUsed, ApiMethodError

__INSTALLED_APPS = {}
__STARTED_APP = None

port_warning = '''
Application {} cannot be started on test port {},
please change port in application settings
'''


def insert_path_to_sys(pth):

    pl = pth.split('/')
    p = '/'.join(pl[:-1])
    sys.path.append(p)
    sys.path.append(pth)

    return pl[-1]   # package name


def check_test_port_is_used(port_to_test, app_name):

    port_to_test = int(port_to_test)
    if port_to_test == TEST_PORT:
        print(port_warning.format(app_name, TEST_PORT))
        sys.exit(3)


def get_installed_apps(installed_apps):

    for app in APPS:

        pkg = insert_path_to_sys(app)
        pm = importlib.import_module(pkg)

        check_test_port_is_used(pm.SVC_PORT, pm.APP_NAME)

        if pm.APP_NAME in installed_apps:
            raise ApplicationNameUsed('{}'.format(pm.APP_NAME))

        installed_apps[pm.APP_NAME] = {}
        installed_apps[pm.APP_NAME]['svc_port'] = pm.SVC_PORT if hasattr(pm, 'SVC_PORT') else None

        global __INSTALLED_APPS
        __INSTALLED_APPS[pm.APP_NAME] = {}
        __INSTALLED_APPS[pm.APP_NAME]['pkg'] = pm
        __INSTALLED_APPS[pm.APP_NAME]['pkg_name'] = pkg


def import_from_settings(imported_modules, app_to_start):

    global __INSTALLED_APPS
    global __STARTED_APP

    __STARTED_APP = __INSTALLED_APPS[app_to_start]
    pkg_dict = __INSTALLED_APPS[app_to_start]
    pm = pkg_dict['pkg']
    base_config.settings.APP_PREFIX = pm.PREFIX

    if hasattr(pm, 'DB_CONF'):
        app_db = importlib.import_module(pm.DB_CONF)
        base_config.settings.APP_DB = app_db.db_config

    if hasattr(pm, 'BASE_TEST'):
        base_config.settings.BASE_TEST = pm.BASE_TEST

    if hasattr(pm, 'LB'):
        base_config.settings.LB = pm.LB
        if base_config.settings.LB:
            if hasattr(pm, 'BALANCE'):
                base_config.settings.BALANCE = pm.BALANCE
            else:
                from base_common.dbaexc import BalancingAppException
                raise BalancingAppException("Missing balancing server ips")

    if hasattr(pm, 'TESTS'):
        base_config.settings.APP_TESTS = pm.TESTS

    if hasattr(pm, 'PREFIX'):
        base_config.settings.APP_TESTS = pm.TESTS

    if hasattr(pm, 'MSG_LOOKUP'):
        _app_msgs = pm.MSG_LOOKUP
        app_msgs = importlib.import_module('{}.{}'.format(pkg_dict['pkg_name'], _app_msgs))
        if hasattr(app_msgs, 'msgs') and isinstance(app_msgs.msgs, dict):
            base_lookup.api_messages.msgs.update(app_msgs.msgs)

    if hasattr(pm, 'APP_HOOKS'):
        hm = importlib.import_module('{}.{}'.format(pkg_dict['pkg_name'], pm.APP_HOOKS))   # import pkg.module
        import base_common.app_hooks
        for h_name in hm.hooks:

            h_attr = getattr(hm, h_name)
            setattr(base_common.app_hooks, h_name, h_attr)

    def _add_to_imports(_mm, _f, _m):

        # _expose = False
        try:
            _expose = getattr(_f, '__api_method_call__')
        except AttributeError:
            return

        if _expose:
            _f_path = _f.__api_path__
            try:
                _f_method = _hm.map[_f.__api_method_type__]
            except KeyError:
                raise ApiMethodError('{} http method is not implemented'.format(_f.__api_method_type__))

            _m_path = '{}/{}'.format(_mm.location, _f_path) if _f_path else _mm.location

            if _m_path not in _m:
                _m[_m_path] = {}

            if _f_method in _m[_m_path]:
                raise ApiMethodError('{} api call already exists in path: {}'.format(_hm.rev[_f_method], _m_path))

            _m[_m_path][_f_method] = _f

            if 'module' not in _m[_m_path]:
                _m[_m_path]['module'] = _mm

    for _m in pm.IMPORTS:
        mm = importlib.import_module('{}.{}'.format(pkg_dict['pkg_name'], _m))   # import pkg.module
        mm.PREFIX = pm.PREFIX       # import pkg settings into module
        mm.APP_NAME = pm.APP_NAME   # import pkg settings into module

        _fs = [o for o in getmembers(mm) if isfunction(o[1])]
        for f in _fs:
            _add_to_imports(mm, f[1], imported_modules)

    for bapp in BASE_APPS:

        base_app = importlib.import_module(bapp)
        for _m in base_app.IMPORTS:

            mm_ = importlib.import_module(_m)   # import base modules
            mm_.BASE = True

            for f in [o for o in getmembers(mm_) if isfunction(o[1])]:
                _add_to_imports(mm_, f[1], imported_modules)


def get_pkgs(pkg_map):

    pkg = __STARTED_APP['pkg']
    pkg_name = __STARTED_APP['pkg_name']

    if hasattr(pkg, 'SHOW_SPECS') and pkg.SHOW_SPECS:

        pkg_map[pkg.APP_NAME] = {}
        pkg_map[pkg.APP_NAME]['PREFIX'] = pkg.PREFIX

        # pkg_map[pkg.APP_NAME]['APP_VERSION'] = pkg.APP_VERSION if hasattr(pkg, 'APP_VERSION') else None
        if hasattr(pkg, 'APP_VERSION'):
            pkg_map[pkg.APP_NAME]['APP_VERSION'] = pkg.APP_VERSION

        for _m in pkg.IMPORTS:
            mm = importlib.import_module('{}.{}'.format(pkg_name, _m))   # import pkg.module
            pkg_map[pkg.APP_NAME][mm.name] = mm

        pkg_map['BASE'] = {}
        pkg_map['BASE']['PREFIX'] = ''

        for bapp in BASE_APPS:

            base_pkg = importlib.import_module(bapp)
            for _m in base_pkg.IMPORTS:
                pk = importlib.import_module(_m)
                pkg_map['BASE'][pk.name] = pk


def get_app():

    return __STARTED_APP
