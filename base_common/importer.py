import sys
import importlib
from base_config.settings import APPS, BASE_APPS, TEST_PORT
import base_config.settings
import base_lookup.api_messages

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

    # base_config.settings.APP_PORT = pm.SVC_PORT

    if hasattr(pm, 'DB_CONF'):
        app_db = importlib.import_module(pm.DB_CONF)
        base_config.settings.APP_DB = app_db.db_config

    if hasattr(pm, 'MSG_LOOKUP'):
        _app_msgs = pm.MSG_LOOKUP
        app_msgs = importlib.import_module('{}.{}'.format(pkg_dict['pkg_name'], _app_msgs))
        if hasattr(app_msgs, 'msgs') and isinstance(app_msgs.msgs, dict):
            base_lookup.api_messages.msgs.update(app_msgs.msgs)

    for _m in pm.IMPORTS:
        mm = importlib.import_module('{}.{}'.format(pkg_dict['pkg_name'], _m))   # import pkg.module
        if mm.name in pm.BASE_EXCEPTIONS:
            continue
        mm.PREFIX = pm.PREFIX       # import pkg settings into module
        mm.APP_NAME = pm.APP_NAME   # import pkg settings into module
        imported_modules.append(mm)

    for bapp in BASE_APPS:

        base_app = importlib.import_module(bapp)
        for _m in base_app.IMPORTS:

            mm_ = importlib.import_module(_m)   # import base modules
            mm_.BASE = True
            imported_modules.append(mm_)


def get_pkgs(pkg_map):

    pkg = __STARTED_APP['pkg']
    pkg_name = __STARTED_APP['pkg_name']

    if hasattr(pkg, 'SHOW_SPECS') and pkg.SHOW_SPECS:

        pkg_map[pkg.APP_NAME] = {}
        pkg_map[pkg.APP_NAME]['PREFIX'] = pkg.PREFIX

        for _m in pkg.IMPORTS:
            mm = importlib.import_module('{}.{}'.format(pkg_name, _m))   # import pkg.module
            if mm.name in pkg.BASE_EXCEPTIONS:
                continue
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
