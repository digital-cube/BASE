import os
import sys
import site
import shutil
import argparse

from config.settings import app_port
from config.settings import template_project_folder
from config.settings import app_builder_description
from config.settings import available_builder_commands


def pars_command_line_argumenst(cmd_args):
    argparser = argparse.ArgumentParser(description=app_builder_description)
    argparser.add_argument('cmd', type=str, help='basemanager command to execute', choices=available_builder_commands)
    argparser.add_argument('-n', '--name', help='the new application name')
    argparser.add_argument('-p', '--port', default=app_port, help='the port for the new application')
    argparser.add_argument('-d', '--destination', default='.', help='the destination directory')
    return argparser.parse_args()


def copy_template(source, destination, tplname):

    import glob

    for _f in glob.glob('{}/*'.format(source)):

        if os.path.isdir(_f):
            dest_path = '{}/{}'.format(destination, os.path.basename(_f))
            shutil.copytree(_f, dest_path)
        else:
            shutil.copy2(_f, destination)


def build_project(args):

    # print('ARGS', args)
    # print('dir', args.destination)

    if not args.name:
        print("CRITICAL: missing project's name, check for option -n")
        sys.exit(1)

    if not os.path.isdir(args.destination):
        print("CRITICAL: missing project's name, check for option -n")
        sys.exit(2)

    try:
        _site_dir = site.getsitepackages()
    except AttributeError as e:
        print('WARNING! can not determine source directory, possible running in virtual environment and it is not handled at the time')
        sys.exit(3)

    dir_path = '{}/{}'.format(args.destination, args.name)
    source_dir = '{}/base/builder/{}'.format(_site_dir[0], template_project_folder)

    try:
        os.mkdir(dir_path)
    except FileExistsError as e:
        print('Directory {} already exists, please provide another name or rename/remove existing one'.format(dir_path))
        sys.exit(4)
    except PermissionError as e:
        print('Can not create {} directory, insufficient permissions'.format(dir_path))
        sys.exit(5)

    copy_template(source_dir, dir_path, args.name)


def init_project(cmd_args):

    parsed_args = pars_command_line_argumenst(cmd_args)

    if parsed_args.cmd == 'init':
        build_project(parsed_args)

