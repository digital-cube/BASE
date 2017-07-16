# coding= utf-8

import os
import sys
import site
import stat
import json
import shutil
import argparse
import importlib
import importlib.util

import sqlalchemy.exc
from inspect import getmembers, isclass
from sqlalchemy.ext.declarative.api import DeclarativeMeta

from base.config.settings import app
from base.config.settings import template_project_folder
from base.config.settings import project_additional_folder
from base.config.settings import app_builder_description
from base.config.settings import app_subcommands_title
from base.config.settings import app_subcommands_description
from base.config.settings import db_init_warning
from base.config.settings import playground_usage
from base.application.lookup import exit_status

import base.common.orm
from base.common.orm import make_database_url


__project_path = None


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
    db_init_parser.add_argument('-p', '--application_port', default=str(app['port'][0]), help=app['port'][1], type=str)
    db_init_parser.add_argument('user_name', type=str, help=app['database_username'][1])
    db_init_parser.add_argument('password', type=str, help=app['database_password'][1])

    db_init_parser = subparsers.add_parser('db_show_create', help="show sql create table query")
    db_init_parser.add_argument('table_name', type=str, help=app['table_name'][1])

    db_init_parser = subparsers.add_parser('playground', help="create api playground frontend with nginx virtual host")

    return argparser.parse_args()


def copy_template(source, destination, project_name):

    import glob

    for _f in glob.glob('{}/*'.format(source)):

        if os.path.isdir(_f):
            dest_path = '{}/{}'.format(destination, os.path.basename(_f))
            shutil.copytree(_f, dest_path)
        else:
            shutil.copy2(_f, destination)

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


def _get_install_directory():

    try:
        _site_dir = site.getsitepackages()
    except AttributeError as e:
        print('''WARNING!
        can not determine source directory,
        possible running in virtual environment and it is not handled at the time
        ''')
        sys.exit(exit_status.MISSING_SOURCE_DIRECTORY)

    return _site_dir


def _create_directory(dir_path):

    try:
        os.mkdir(dir_path)
    except FileExistsError as e:
        print('Directory {} already exists, please provide another name or rename/remove existing one'.format(dir_path))
        sys.exit(exit_status.PROJECT_DIRECTORY_ALREADY_EXISTS)
    except PermissionError as e:
        print('Can not create {} directory, insufficient permissions'.format(dir_path))
        sys.exit(exit_status.PROJECT_DIRECTORY_PERMISSION_ERROR)


def _build_project(args):

    if not args.name:
        print("CRITICAL: missing project's name, check for option -n")
        sys.exit(exit_status.MISSING_PROJECT_NAME)

    if not os.path.isdir(args.destination):
        print("CRITICAL: missing project's name, check for option -n")
        sys.exit(exit_status.MISSING_PROJECT_DESTINATION)

    _site_dir = _get_install_directory()
    dir_path = '{}/{}'.format(args.destination, args.name)
    source_dir = '{}/base/builder/{}'.format(_site_dir[0], template_project_folder)
    additions_dir = '{}/base/builder/{}'.format(_site_dir[0], project_additional_folder)
    _create_directory(dir_path)

    copy_template(source_dir, dir_path, args.name)

    _configure_project(args, dir_path, additions_dir)


def _configure_database(args, app_config, _db_config, test=False):

    __dest_dir = os.path.dirname(app_config.__file__)
    __db_config_file = '{}/{}'.format(__dest_dir, app_config.db_config)

    if not os.path.isfile(__db_config_file):
        print('Create database configuration for application port {}'.format(args.application_port))
    else:
        if not test:
            print('Update database configuration with application port {}'.format(args.application_port))
        with open(__db_config_file) as _db_cfg:
            try:
                _db_conf = json.load(_db_cfg)
                for _k in _db_conf:
                    _db_config[_k] = _db_conf[_k]
            except json.JSONDecodeError:
                pass

    if not test:
        _db_config[args.application_port] = {
            'db_name': args.database_name,
            'db_user': args.user_name,
            'db_password': args.password,
            'db_host': args.database_host,
            'db_type': args.database_type,
        }

        try:
            _db_config[args.application_port]['db_port'] = args.database_port if args.database_port else \
                str(app['database_port'][0][args.database_type])
        except KeyError as e:
            print('Wrong database type configured: {}'.format(args.database_type))
            return False

        with open(__db_config_file, 'w') as _db_cfg:
            _db_cfg.write(json.dumps(_db_config, ensure_ascii=False, sort_keys=True, indent=4))

    return True


def __db_is_configured(args, test):

    try:
        import src.config.app_config
    except ImportError as e:
        print('Can not find application configuration')
        return False, False

    if not hasattr(src.config.app_config, 'db_config'):
        print('Missing Database configuration in config file')
        return False, False

    __db_config = {}
    if not _configure_database(args, src.config.app_config, __db_config, test):
        print('Error configuring database')
        return False, False

    __port = str(src.config.app_config.port) if test else args.application_port

    if __port not in __db_config:
        print('Missing database configuration for port: {}'.format(__port))
        return False, False
    __db_config = __db_config[__port]
    __db_type = __db_config['db_type']

    for k in __db_config:

        if __db_config[k].startswith('__') or __db_config[k].endswith('__'):
            print("Database not properly configured: the {} can not be '{}'".format(k, __db_config[k]))
            return False, False

    return __db_config, __db_type


def _get_orm_models(models_list, orm_models):
    for m in orm_models:
        try:
            _m = importlib.import_module(m)
            models_list.append(_m)
        except ImportError:
            print('Error loading model {}'.format(m))


def _update_path():

    _project_path = os.getcwd()
    sys.path.append(_project_path)


def _build_database(args, test=False):

    _update_path()

    db_config, db_type = __db_is_configured(args, test)
    if not db_config:
        sys.exit(exit_status.DATABASE_CONFIGURATION_ERROR)

    _database_name = 'test_{}'.format(db_config['db_name']) if test else db_config['db_name']
    __db_url = make_database_url(db_type, _database_name, db_config['db_host'], db_config['db_port'],
                                 db_config['db_user'], db_config['db_password'])

    import base.common.orm
    orm_builder = base.common.orm.orm_builder(__db_url, base.common.orm.sql_base)
    setattr(base.common.orm, 'orm', orm_builder.orm())

    import src.config.app_config
    if not hasattr(src.config.app_config, 'models'):
        print('Nothing to be done')
        return

    # PRESENT MODELS TO BASE
    _models_modules = []
    _get_orm_models(_models_modules, src.config.app_config.models)

    try:
        orm_builder.create_db_schema()
    except sqlalchemy.exc.OperationalError:
        print('Database {} is missing, please create it'.format(args.database_name))
        sys.exit(exit_status.DATABASE_INITIALIZATION_ERROR)

    def _get_sequnecer_model_module(_models_modules):

        for m in _models_modules:
            if 'sequencer' in m.__name__:
                _models_modules.remove(m)
                return m

    # LOAD ORM FOR SEQUENCERS IN MODELS
    from base.application.helpers.importer import load_orm
    import base.config.application_config
    setattr(base.config.application_config, 'models', src.config.app_config.models)
    load_orm(args.application_port)

    # PREPARE SEQUENCERS FIRST
    _seq_module = _get_sequnecer_model_module(_models_modules)
    if _seq_module:
        _seq_module.main()

    # PREPARE DATABASE
    for m in _models_modules:
        try:
            m.main()
        except AttributeError:
            print(m.__name__, "doesn't have to be prepared")

        except sqlalchemy.exc.IntegrityError:
            print('Database {} already exists, please recreate it'.format(args.database_name))
            sys.exit(exit_status.DATABASE_INITIALIZATION_ERROR)

    if not test:
        print('Database {} created successfully'.format(args.database_name))

    return orm_builder


def _show_create_table(args):

    _update_path()

    src = 'src/config/app_config.py'
    if not os.path.isfile(src):
        print(db_init_warning)
        sys.exit(exit_status.MISSING_PROJECT_CONFIGURATION)

    import src.config.app_config
    if not hasattr(src.config.app_config, 'models'):
        print('No orm models in configuration file')
        sys.exit(exit_status.MISSING_ORM_MODELS)

    if not hasattr(src.config.app_config, 'db_config'):
        print('No database configuration in configuration file')
        sys.exit(exit_status.MISSING_DATABASE_CONFIGURATION)

    __dest_dir = os.path.dirname(src.config.app_config.__file__)
    __db_config_file = '{}/{}'.format(__dest_dir, src.config.app_config.db_config)
    db_config = {}
    with open(__db_config_file) as _db_cfg:
        try:
            db_config = json.load(_db_cfg)
        except json.JSONDecodeError:
            print('Can not load database configuration')
            sys.exit(exit_status.DATABASE_NOT_CONFIGURED)

    _models_modules = []
    _get_orm_models(_models_modules, src.config.app_config.models)

    _port = str(src.config.app_config.port)
    if _port not in db_config:
        print('Missing database configuration for port: {}'.format(_port))
        sys.exit(exit_status.DATABASE_NOT_CONFIGURED)

    _db_config = db_config[_port]
    db_type = _db_config['db_type']

    __db_url = make_database_url(db_type, _db_config['db_name'], _db_config['db_host'], _db_config['db_port'],
                                 _db_config['db_user'], _db_config['db_password'])

    orm_builder = base.common.orm.orm_builder(__db_url, base.common.orm.sql_base)

    # PREPARE DATABASE

    _orm_model = None
    for m in _models_modules:

        break1 = False
        for _name, _model in getmembers(m, isclass):
            if type(_model) == DeclarativeMeta and hasattr(_model, '__table__'):
                if _model.__table__.name == args.table_name:
                    _orm_model = _model
                    break1 = True
                    break
        if break1:
            break

    if _orm_model is None:
        print('Table {} has no model, or model not configured'.format(args.table_name))
        sys.exit(exit_status.TABLE_NOT_PRESENT)

    _db_engine = orm_builder.orm().engine()
    from sqlalchemy.schema import CreateTable
    _create_table_query = CreateTable(_orm_model.__table__).compile(_db_engine)
    print('{} table create query:\n'.format(args.table_name))
    print(_create_table_query)


def _create_playground(parsed_args):

    _playground = 'playground'

    _site_dir = _get_install_directory()
    source_dir = '{}/base/builder/{}'.format(_site_dir[0], _playground)

    try:
        shutil.copytree(source_dir, _playground)
    except FileExistsError as e:
        print('Directory {} already exists, please rename/remove existing one'.format(_playground))
        sys.exit(exit_status.PROJECT_DIRECTORY_ALREADY_EXISTS)
    except PermissionError as e:
        print('Can not create {} directory, insufficient permissions'.format(_playground))
        sys.exit(exit_status.PROJECT_DIRECTORY_PERMISSION_ERROR)

    print(playground_usage)


def execute_builder_cmd():

    parsed_args = pars_command_line_arguments()

    if parsed_args.cmd == 'init':
        _build_project(parsed_args)

    if parsed_args.cmd == 'db_init':
        _build_database(parsed_args)

    if parsed_args.cmd == 'db_show_create':
        _show_create_table(parsed_args)

    if parsed_args.cmd == 'playground':
        _create_playground(parsed_args)
