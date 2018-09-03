import os
import sys
import site
import json
import shutil
import importlib

from base.application.lookup import exit_status
from base.config.settings import models_config_file


def get_install_directory():

    try:
        _site_dir = site.getsitepackages()
    except AttributeError as e:
        print('''WARNING!
        can not determine source directory,
        possible running in virtual environment and it is not handled at the time
        ''')
        sys.exit(exit_status.MISSING_SOURCE_DIRECTORY)

    return _site_dir


def update_path():

    _project_path = os.getcwd()
    sys.path.append(_project_path)


def get_orm_models(models_list, app_config):
    try:
        models_file = '{}/{}'.format(os.path.dirname(app_config.__file__), models_config_file)
        with open(models_file) as mf:
            orm_models = json.load(mf)
    except FileNotFoundError:
        # for compatibility with the BASE version < 1.2.0
        orm_models = app_config.models if hasattr(app_config, 'models') else []

    for m in orm_models:
        try:
            _m = importlib.import_module(m)
            models_list.append(_m)
        except ImportError:
            print('Error loading model {}'.format(m))

    return orm_models


def copy_dir(source, destination):
    try:
        shutil.copytree(source, destination)
    except FileExistsError as e:
        print('Directory "{}" already exists, using existing resource'.format(destination))
    except PermissionError as e:
        print('Can not create directory "{}", insufficient permissions'.format(destination))
        sys.exit(exit_status.PROJECT_DIRECTORY_PERMISSION_ERROR)


def copy_file(source_file, destination_file):

    try:
        shutil.copy(source_file, destination_file)
    except FileExistsError as e:
        print('File "{}" already exists, using existing one'.format(destination_file))
    except PermissionError as e:
        print('Can not create "{}", insufficient permissions'.format(destination_file))
        sys.exit(exit_status.FILE_PERMISSION_ERROR)

