import os
import sys
import stat
import shutil
import platform

from base.builder.maker.common import get_install_directory
from base.application.lookup import exit_status
from base.config.settings import template_project_folder
from base.config.settings import project_additional_folder

__WINDOWS__ = platform.system() == 'Windows'


def _create_directory(dir_path):

    try:
        os.mkdir(dir_path)
    except FileExistsError as e:
        print('Directory {} already exists, please provide another name or rename/remove existing one'.format(dir_path))
        sys.exit(exit_status.PROJECT_DIRECTORY_ALREADY_EXISTS)
    except PermissionError as e:
        print('Can not create {} directory, insufficient permissions'.format(dir_path))
        sys.exit(exit_status.PROJECT_DIRECTORY_PERMISSION_ERROR)


def copy_template(source, destination, project_name):

    import glob

    for _f in glob.glob('{}/*'.format(source)):

        if os.path.isdir(_f):
            dest_path = '{}/{}'.format(destination, os.path.basename(_f))
            shutil.copytree(_f, dest_path)
        else:
            shutil.copy2(_f, destination)

    os.makedirs('{}/log'.format(destination))
    open('{}/log/.gitkeep'.format(destination), 'w+')
    os.makedirs('{}/tests/log'.format(destination))
    open('{}/tests/log/.gitkeep'.format(destination), 'w+')

    git_ignore = '{}/{}'.format(source, '.gitignore')
    if os.path.isfile(git_ignore):
        shutil.copy2(git_ignore, destination)

    # RENAME A PROJECT RUNNER INTO THE NAME OF THE PROJECT
    _src = '{}/starter.py'.format(destination)
    _dst = '{}/{}'.format(destination, project_name)
    shutil.move(_src, _dst)

    st = os.stat(_dst)
    os.chmod(_dst, st.st_mode | stat.S_IEXEC)


def _configure_project(args, destination, additions_dir):

    _project_conf_source = '{}/app_config.py'.format(additions_dir)
    _project_conf_file = '{}/src/config/app_config.py'.format(destination)

    with open(_project_conf_file, 'w') as _new_config:
        with open(_project_conf_source) as _source_file:

            for _line in _source_file:
                if '__APP_NAME__' in _line:
                    _line = "app_name = '{}'\n".format(args.name)
                if '__APP_DESCRIPTION__' in _line:
                    _line = "app_description = '{}'\n".format(args.description)
                if '__PORT__' in _line:
                    _line = 'port = {}\n'.format(args.port)
                if '__APP_PREFIX__' in _line:
                    _line = "app_prefix = '{}'\n".format(args.prefix)
                if '__APP_VERSION__' in _line:
                    _line = "app_version = '{}'\n".format(args.version)

                _new_config.write(_line)


def build_project(args):

    if not args.name:
        print("CRITICAL: missing project's name, check for option -n")
        sys.exit(exit_status.MISSING_PROJECT_NAME)

    if not os.path.isdir(args.destination):
        print("CRITICAL: missing project's name, check for option -n")
        sys.exit(exit_status.MISSING_PROJECT_DESTINATION)

    _site_dir = get_install_directory()
    dir_path = '{}/{}'.format(args.destination, args.name)
    source_dir = '{}/base/builder/{}'.format(_site_dir[1] if __WINDOWS__ else _site_dir[0], template_project_folder)
    additions_dir = '{}/base/builder/{}'.format(_site_dir[1] if __WINDOWS__ else _site_dir[0], project_additional_folder)
    _create_directory(dir_path)

    copy_template(source_dir, dir_path, args.name)

    _configure_project(args, dir_path, additions_dir)

