# coding= utf-8

import os
import sys
import site
import shutil
import argparse

from base.config.settings import app
from base.config.settings import template_project_folder
from base.config.settings import project_additional_folder
from base.config.settings import app_builder_description
from base.config.settings import available_builder_commands


def pars_command_line_arguments():

    argparser = argparse.ArgumentParser(description=app_builder_description)
    argparser.add_argument('cmd', type=str, help=app['cmd'][1], choices=available_builder_commands)
    argparser.add_argument('-n', '--name', help=app['name'][1])
    argparser.add_argument('-D', '--destination', default=app['destination'][0], help=app['destination'][1])
    argparser.add_argument('-d', '--description', default=app['description'][0], help=app['description'][1])
    argparser.add_argument('-p', '--port', default=app['port'][0], help=app['port'][1])
    argparser.add_argument('-v', '--version', default=app['version'][0], help=app['version'][1])
    argparser.add_argument('-x', '--prefix', default=app['prefix'][0], help=app['prefix'][1])
    return argparser.parse_args()


def copy_template(source, destination):

    import glob

    for _f in glob.glob('{}/*'.format(source)):

        if os.path.isdir(_f):
            dest_path = '{}/{}'.format(destination, os.path.basename(_f))
            shutil.copytree(_f, dest_path)
        else:
            shutil.copy2(_f, destination)


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


def _build_project(args):

    if not args.name:
        print("CRITICAL: missing project's name, check for option -n")
        sys.exit(1)

    if not os.path.isdir(args.destination):
        print("CRITICAL: missing project's name, check for option -n")
        sys.exit(2)

    try:
        _site_dir = site.getsitepackages()
    except AttributeError as e:
        print('''WARNING!
        can not determine source directory,
        possible running in virtual environment and it is not handled at the time
        ''')
        sys.exit(3)

    dir_path = '{}/{}'.format(args.destination, args.name)
    source_dir = '{}/base/builder/{}'.format(_site_dir[0], template_project_folder)
    additions_dir = '{}/base/builder/{}'.format(_site_dir[0], project_additional_folder)

    try:
        os.mkdir(dir_path)
    except FileExistsError as e:
        print('Directory {} already exists, please provide another name or rename/remove existing one'.format(dir_path))
        sys.exit(4)
    except PermissionError as e:
        print('Can not create {} directory, insufficient permissions'.format(dir_path))
        sys.exit(5)

    copy_template(source_dir, dir_path)

    _configure_project(args, dir_path, additions_dir)


def execute_builder_cmd():

    parsed_args = pars_command_line_arguments()

    if parsed_args.cmd == 'init':
        _build_project(parsed_args)

