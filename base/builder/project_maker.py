# coding= utf-8

import os
import sys
import site
import shutil
import tempfile
import argparse
import importlib

from base.config.settings import app
from base.config.settings import template_project_folder
from base.config.settings import project_additional_folder
from base.config.settings import app_builder_description
from base.config.settings import app_subcommands_title
from base.config.settings import app_subcommands_description
from base.config.settings import db_init_warning

import common.orm
from common.orm import make_database_url


def pars_command_line_arguments():

    argparser = argparse.ArgumentParser(description=app_builder_description)

    subparsers = argparser.add_subparsers(title=app_subcommands_title, description=app_subcommands_description,
                                          help='choose from available commands', dest='cmd')
    subparsers.required = True

    init_parser = subparsers.add_parser('init', help='initialize base project')
    init_parser.add_argument('name', type=str, help=app['name'][1])
    init_parser.add_argument('-D', '--destination', default=app['destination'][0], help=app['destination'][1])
    init_parser.add_argument('-d', '--description', default=app['description'][0], help=app['description'][1])
    init_parser.add_argument('-p', '--port', default=app['port'][0], help=app['port'][1])
    init_parser.add_argument('-v', '--version', default=app['version'][0], help=app['version'][1])
    init_parser.add_argument('-x', '--prefix', default=app['prefix'][0], help=app['prefix'][1])

    db_init_parser = subparsers.add_parser('db_init', help="create base project's database schema")
    db_init_parser.add_argument('-dt', '--database_type', default=app['database_type'][0], help=app['database_type'][1])
    db_init_parser.add_argument('-dn', '--database_name', default=os.getcwd().split('/')[-1],
                                help=app['database_name'][1])
    db_init_parser.add_argument('-dh', '--database_host', default=app['database_host'][0], help=app['database_host'][1])
    db_init_parser.add_argument('-dp', '--database_port', help=app['database_port'][1])
    db_init_parser.add_argument('user_name', type=str, help=app['database_username'][1])
    db_init_parser.add_argument('password', type=str, help=app['database_password'][1])

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
                if '__APP_DB_NAME__' in _line:
                    _line = _line.replace('__APP_DB_NAME__', "'{}'".format(args.name))

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


def _configure_database(args):

    src = 'src/config/app_config.py'
    if not os.path.isfile(src):
        print('Missing configuration file')
        return False

    tmp_dir = tempfile.gettempdir()
    tmp_filename = 'app_tmp.py'
    tmp_f = os.path.join(tmp_dir, tmp_filename)
    import shutil
    shutil.copy2(src, tmp_f)

    _tab = '    '

    with open(tmp_f) as tf:
        with open(src, 'w') as cf:

            for _line in tf:

                if "db_type" in _line and args.database_type:
                    _line = "db_type = '{}',\n".format(args.database_type)
                if "'db_name'" in _line and args.database_name:
                    _line = "{}'db_name': '{}',\n".format(_tab, args.database_name)
                if "'db_user'" in _line and args.user_name:
                    _line = "{}'db_user': '{}',\n".format(_tab, args.user_name)
                if "'db_password'" in _line and args.password:
                    _line = "{}'db_password': '{}',\n".format(_tab, args.password)
                if "'db_host'" in _line and args.database_host:
                    _line = "{}'db_host': '{}',\n".format(_tab, args.database_host)
                if "'db_port'" in _line:
                    try:
                        port = args.database_port if args.database_port else\
                            app['database_port'][0][args.database_type]
                    except KeyError as e:
                        print('Wrong database type configured: {}'.format(args.database_type))
                        return False

                    _line = "{}'db_port': '{}',\n".format(_tab, port)

                cf.write(_line)

    return True


def __db_is_configured(args):

    try:
        from starter import engage
    except ImportError as e:
        print(db_init_warning)
        return False

    if not _configure_database(args):
        print('Error configuring database')
        return False

    try:
        import src.config.app_config
    except ImportError as e:
        print('Can not find application configuration')
        return False

    if not hasattr(src.config.app_config, 'db_config'):
        print('Missing Database configuration in config file')
        return False

    __db_config = src.config.app_config.db_config

    for k in __db_config:

        if __db_config[k].startswith('__') or __db_config[k].endswith('__'):
            print("Database not properly configured: the {} can not be '{}'".format(k, __db_config[k]))
            return False

    return __db_config


def _build_database(args):

    db_config = __db_is_configured(args)
    if not db_config:
        sys.exit(6)

    __db_url = make_database_url(args.database_type, db_config['db_name'], db_config['db_host'], db_config['db_port'],
                                 db_config['db_user'], db_config['db_password'])

    orm_builder = common.orm.orm_builder(__db_url, common.orm.sql_base)

    import src.config.app_config
    if not hasattr(src.config.app_config, 'models'):
        print('Nothing to be done')
        return

    # PRESENT MODELS TO BASE
    for m in src.config.app_config.models:
        try:
            importlib.import_module(m)
        except ImportError:
            print('Error loading model {}'.format(m))

    orm_builder.create_db_schema()


def execute_builder_cmd():

    parsed_args = pars_command_line_arguments()

    if parsed_args.cmd == 'init':
        _build_project(parsed_args)

    if parsed_args.cmd == 'db_init':
        _build_database(parsed_args)

