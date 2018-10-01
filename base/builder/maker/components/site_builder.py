import os
import sys
import json
import importlib

from base.application.lookup import exit_status
from base.builder.maker.common import update_path
from base.builder.maker.common import get_install_directory
from base.builder.maker.common import copy_dir
from base.builder.maker.common import copy_file
from base.common.orm import init_orm
from base.config.settings import models_config_file


def _add_modules_to_config(config_file):

    # edit application config file and add site API
    with open(config_file, 'r') as cf:
        _file = cf.readlines()

    _new_file = []

    for _line in _file:

        if _line[:11] == 'imports = [':
            _new_file.append(_line)
            _new_file.append("    'src.api.site.site',\n")
            continue

        _new_file.append(_line)

    with open(config_file, 'w') as cf:

        cf.write(''.join(_new_file))

    return True


def _add_tests(app_config):

    test_dir = os.path.abspath(os.path.join(os.path.dirname(app_config.__file__), '../../tests'))
    tests_file = '{}/start_all_tests.py'.format(test_dir)

    if os.path.isdir(test_dir) and os.path.isfile(tests_file):

        with open(tests_file, 'r') as tf:
            _file = tf.readlines()

        _new_file = []

        for _line in _file:

            if 'tests.hello' in _line:
                _new_file.append(_line)
                _new_file.append("from tests.site_tests import TestSite\n")
                continue

            _new_file.append(_line)

        with open(tests_file, 'w') as tf:

            tf.write(''.join(_new_file))
    else:
        print('Please update tests with new site_tests ')


def add_site():

    update_path()
    try:
        import src.config.app_config
    except ImportError as e:
        print('Can not find application configuration')
        sys.exit(exit_status.MISSING_PROJECT_CONFIGURATION)

    if not hasattr(src.config.app_config, 'db_config'):
        print('Missing Database configuration in config file, please initialize database first')
        sys.exit(exit_status.MISSING_DATABASE_CONFIGURATION)

    # check if config file has active models, and update models with site models
    import src.config.app_config
    models_file = '{}/{}'.format(os.path.dirname(src.config.app_config.__file__), models_config_file)
    models_directory = '{}/{}'.format(os.path.abspath(os.path.join(os.path.dirname(src.config.app_config.__file__), '..')), 'models')

    if not os.path.isdir(models_directory) or \
            (not os.path.isfile(models_file) and not hasattr(src.config.app_config, 'models')):
                print('Models not initialized, please execute db_init first')
                sys.exit(exit_status.MISSING_DATABASE_CONFIGURATION)

    if not os.path.isfile(models_file) and hasattr(src.config.app_config, 'models'):
        print('Models defined in config file, please update models in application config file with site model')
    else:

        with open(models_file) as mf:
            models = json.load(mf)
        if any(list(map(lambda m: 'site' in m, models))):
            print('Models should contain site module, please check configuration')
        else:
            models.append('src.models.site')
            with open(models_file, 'w') as mf:
                json.dump(models, mf, indent=4, sort_keys=True, ensure_ascii=False)

    # copy models for site
    _site_dir = get_install_directory()
    _destination_file = 'src/models/site.py'
    models_additional_source_dir = '{}/base/builder/project_additional/models_additional'.format(_site_dir[0])
    models_file = '{}/site.py'.format(models_additional_source_dir)
    copy_file(models_file, _destination_file)

    # create tables for site
    orm_builder = init_orm()
    import base.common.orm
    setattr(base.common.orm, 'orm', orm_builder.orm())
    orm_builder.add_blog()
    try:
        _m = importlib.import_module('src.models.site')
        _m.main()
    except ImportError:
        print('Error loading model {}, please execute the main manually'.format(src.models.site.__file__))

    # check if api exists, if not copy it from the repo
    api_source_dir = '{}/base/builder/project_additional/api/site'.format(_site_dir[0])
    copy_dir(api_source_dir, 'src/api/site')

    # update app config with api paths
    _add_modules_to_config(src.config.app_config.__file__)

    # add tests for site
    test_source = '{}/base/builder/project_additional/tests/site_tests.py'.format(_site_dir[0])
    copy_file(test_source, 'tests/site_tests.py')
    _add_tests(src.config.app_config)

    print('site component is in the system')

