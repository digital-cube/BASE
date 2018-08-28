# coding= utf-8

import os
import sys
import site
import stat
import json
import shutil
import argparse
import platform
import importlib
import importlib.util

import sqlalchemy.exc
from inspect import getmembers, isclass
from sqlalchemy.ext.declarative.api import DeclarativeMeta

import base

from base.config.settings import app
from base.config.settings import models_config_file
from base.config.settings import template_project_folder
from base.config.settings import project_additional_folder
from base.config.settings import app_builder_description
from base.config.settings import app_subcommands_title
from base.config.settings import app_subcommands_description
from base.config.settings import db_init_warning
from base.config.settings import playground_usage
from base.config.settings import available_BASE_components
from base.config.settings import default_models
from base.application.lookup import exit_status

import base.common.orm
from base.common.orm import make_database_url
from base.common.orm import make_database_url2
from base.common.orm import init_orm


__project_path = None
__WINDOWS__ = platform.system() == 'Windows'


def pars_command_line_arguments():

    argparser = argparse.ArgumentParser(description=app_builder_description)

    subparsers = argparser.add_subparsers(title=app_subcommands_title, description=app_subcommands_description,
                                          help='choose from available commands', dest='cmd')
    subparsers.required = True

    init_parser = subparsers.add_parser('init', help='initialize base project', aliases=['i'])
    init_parser.add_argument('name', type=str, help=app['name'][1])
    init_parser.add_argument('-D', '--destination', default=app['destination'][0], help=app['destination'][1])
    init_parser.add_argument('-d', '--description', default=app['description'][0], help=app['description'][1])
    init_parser.add_argument('-p', '--port', default=app['port'][0], help=app['port'][1])
    init_parser.add_argument('-v', '--version', default=app['version'][0], help=app['version'][1])
    init_parser.add_argument('-x', '--prefix', default=app['prefix'][0], help=app['prefix'][1])

    _splitter = '\\' if __WINDOWS__ else '/'
    db_init_parser = subparsers.add_parser('db_init', help="create base project's database schema", aliases=['dbi'])
    db_init_parser.add_argument('-dt', '--database_type', default=app['database_type'][0], help=app['database_type'][1])
    db_init_parser.add_argument('-dn', '--database_name', default=os.getcwd().split(_splitter)[-1],
                                help=app['database_name'][1])
    db_init_parser.add_argument('-dh', '--database_host', default=app['database_host'][0], help=app['database_host'][1])
    db_init_parser.add_argument('-dp', '--database_port', help=app['database_port'][1])
    db_init_parser.add_argument('-p', '--application_port', help=app['port'][1], type=str)
    db_init_parser.add_argument('-a', '--add_action_logs', default=app['add_action_logs'][0],
                                help=app['add_action_logs'][1], type=bool)
    db_init_parser.add_argument('user_name', type=str, help=app['database_username'][1])
    db_init_parser.add_argument('password', type=str, help=app['database_password'][1])

    show_create_parser = subparsers.add_parser('db_show_create', help="show sql create table query", aliases=['dbs'])
    show_create_parser.add_argument('table_name', type=str, help=app['table_name'][1])

    playground_parser = subparsers.add_parser('playground',
                                              help="create api playground frontend with nginx virtual host",
                                              aliases=['p'])

    add_plugin_parser = subparsers.add_parser('add', help="add a component to the BASE project", aliases=['a'])
    add_plugin_parser.add_argument('component', type=str, help=app['component'][1])

    list_plugins_parser = subparsers.add_parser('list', help="list available BASE components", aliases=['l'])

    argparser.add_argument('-V', '--version', action='version', help='show BASE version', version='BASE v{}'.format(base.__VERSION__))

    return argparser.parse_args()


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
    source_dir = '{}/base/builder/{}'.format(_site_dir[1] if __WINDOWS__ else _site_dir[0], template_project_folder)
    additions_dir = '{}/base/builder/{}'.format(_site_dir[1] if __WINDOWS__ else _site_dir[0], project_additional_folder)
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


def _enable_database_in_config(config_file, args, test):

    # create models config file
    models_file = '{}/{}'.format(os.path.dirname(config_file), models_config_file)
    with open(models_file, 'w') as mf:
        json.dump(default_models, mf, indent=4, sort_keys=True, ensure_ascii=False)

    # edit application config file and enable database features
    with open(config_file, 'r') as cf:
        _file = cf.readlines()

    _new_file = []
    _forgot = False
    _max_forgot_try = 20

    for _line in _file:

        if _max_forgot_try == 0:
            print('MAXIMUM TRIES EXCEEDED')
            break

        if _line[:11] == '# db_config':
            _new_file.append(_line[2:])
            continue

        if _line[:11] == '# api_hooks':
            _new_file.append(_line[2:])
            continue

        if _line[:17] == '# session_storage':
            _new_file.append(_line[2:])
            continue

        if _line[:19] == '# user_roles_module':
            _new_file.append(_line[2:])
            continue

        if _line[:17] == '# strong_password':
            _new_file.append(_line[2:])
            continue

        if _line[:33] == '# forgot_password_lending_address':
            _new_file.append(_line[2:])
            continue

        if _line[:33] == '# forgot_password_message_subject':
            _new_file.append(_line[2:])
            continue

        if _forgot and _line != "# '''\n":
            _new_file.append(_line[2:])
            _max_forgot_try -= 1
            continue

        if _line == "# forgot_password_message = '''\n":
            _new_file.append(_line[2:])
            _forgot = True
            continue

        if _forgot and _line == "# '''\n":
            _new_file.append(_line[2:])
            _forgot = False
            continue

        _new_file.append(_line)

    with open(config_file, 'w') as cf:

        cf.write(''.join(_new_file))

    return True


def __db_is_configured(args, test):

    try:
        import src.config.app_config
    except ImportError as e:
        print('Can not find application configuration')
        return False, False

    if not _enable_database_in_config(src.config.app_config.__file__, args, test):
        print('Can not configure Database in the application')
        return False, False

    # reimport configuration file
    try:
        importlib.reload(src.config.app_config)
    except ImportError as e:
        print('Can not reload application configuration')
        return False, False

    # set application port in args from configuration if not present in args
    if args.application_port is None:
        args.application_port = src.config.app_config.port

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


def _get_orm_models(models_list, app_config):
    models_file = '{}/{}'.format(os.path.dirname(app_config.__file__), models_config_file)
    with open(models_file) as mf:
        orm_models = json.load(mf)
    for m in orm_models:
        try:
            _m = importlib.import_module(m)
            models_list.append(_m)
        except ImportError:
            print('Error loading model {}'.format(m))

    return orm_models


def _update_path():

    _project_path = os.getcwd()
    sys.path.append(_project_path)


def _copy_database_components(args, db_type, db_name, db_config):

    _site_dir = _get_install_directory()
    alembic_dir = '{}/base/builder/project_additional/db'.format(_site_dir[0])
    models_source_dir = '{}/base/builder/project_additional/models'.format(_site_dir[0])
    models_additional_source_dir = '{}/base/builder/project_additional/models_additional'.format(_site_dir[0])
    hooks_source_dir = '{}/base/builder/project_additional/api_hooks'.format(_site_dir[0])

    _show_info = True

    # copy alembic environment
    try:
        shutil.copytree(alembic_dir, 'db')

        # update alembic configuration
        new_alembic_ini = ''
        _write = False
        with open('db/alembic.ini') as alembic_ini:
            for _line in alembic_ini:
                if _line[:14] == 'sqlalchemy.url':
                    _line = 'sqlalchemy.url = {}://{}:{}@{}/{}\n'.format(
                        db_type, db_config['db_user'], db_config['db_password'], db_config['db_host'], db_name)
                    _write = True

                new_alembic_ini += '{}'.format(_line)

        if _write:
            with open('db/alembic.ini', 'w') as alembic_ini:
                alembic_ini.write(new_alembic_ini)

    except FileExistsError as e:
        print('Directory "db" already exists, using existing alembic structure')
        _show_info = False
    except PermissionError as e:
        print('Can not create directory "db", insufficient permissions')
        sys.exit(exit_status.PROJECT_DIRECTORY_PERMISSION_ERROR)

    # copy models
    try:
        shutil.copytree(models_source_dir, 'src/models')
    except FileExistsError as e:
        print('Directory "src/models" already exists, using existing models')
        _show_info = False
    except PermissionError as e:
        print('Can not create directory "src/models", insufficient permissions')
        sys.exit(exit_status.PROJECT_DIRECTORY_PERMISSION_ERROR)

    # copy activity model if configured
    if args.add_action_logs:

        try:
            shutil.copy('{}/activity.py'.format(models_additional_source_dir), 'src/models/activity.py')
        except FileExistsError as e:
            print('Model "src/models/activity" already exists, using existing one')
            _show_info = False
        except PermissionError as e:
            print('Can not create "src/model/activity.py", insufficient permissions')
            sys.exit(exit_status.FILE_PERMISSION_ERROR)

    # copy hooks
    try:
        shutil.copytree(hooks_source_dir, 'src/api_hooks')
    except FileExistsError as e:
        print('Directory "src/api_hooks" already exists, using existing one')
        _show_info = False
    except PermissionError as e:
        print('Can not create directory "src/api_hooks", insufficient permissions')
        sys.exit(exit_status.PROJECT_DIRECTORY_PERMISSION_ERROR)

    if _show_info:
        print('Database models shown')

    return True


def _create_database(db_name, db_type, db_config, test=False):

    from sqlalchemy import create_engine
    if db_type == 'sqlite':
        return True
    else:
        # def make_database_url2(db_type, host, port, username, password, charset='utf8'):
        # _url = '{}://{}:{}@{}:{}'.format(
        #     db_type, db_config['db_user'], db_config['db_password'], db_config['db_host'], db_config['db_port'])
        _url = make_database_url2(
            db_type, db_config['db_host'], db_config['db_port'], db_config['db_user'], db_config['db_password'])
        eng = create_engine(_url)

    if db_type == 'postgresql':
        existing_databases = eng.execute('select datname from pg_database')
    else:
        existing_databases = eng.execute('show databases;')

    existing_databases = [db[0] for db in existing_databases]
    _db_exists = any([dbn == db_name for dbn in existing_databases])

    if _db_exists:
        if not test:
            print('Found database {}'.format(db_name))
    else:
        print('Database {} not found, will be created'.format(db_name))
        conn = eng.connect()
        conn.execute('commit')
        conn.execute('create database {}'.format(db_name))
        conn.close()
        print('Database {} created'.format(db_name))

    return True


def _build_database(args, test=False):

    _update_path()

    db_config, db_type = __db_is_configured(args, test)
    if not db_config:
        sys.exit(exit_status.DATABASE_CONFIGURATION_ERROR)

    _database_name = 'test_{}'.format(db_config['db_name']) if test else db_config['db_name']
    __db_url = make_database_url(db_type, _database_name, db_config['db_host'], db_config['db_port'],
                                 db_config['db_user'], db_config['db_password'],
                                 db_config['charset'] if 'charset' in db_config else 'utf8')

    import base.common.orm
    orm_builder = base.common.orm.orm_builder(__db_url, base.common.orm.sql_base)
    setattr(base.common.orm, 'orm', orm_builder.orm())

    if not _create_database(_database_name, db_type, db_config, test):
        print('Database has not created')
        return

    import src.config.app_config
    models_file = '{}/{}'.format(os.path.dirname(src.config.app_config.__file__), models_config_file)
    if not os.path.isfile(models_file) and not hasattr(src.config.app_config, 'models'):
        print('Nothing to be done')
        return

    if not test and not _copy_database_components(args, db_type, _database_name, db_config):
        print('Can not initialize database components')
        return

    # PRESENT MODELS TO BASE
    _models_modules = []
    _orm_models = _get_orm_models(_models_modules, src.config.app_config)

    if test:
        # teardown database in test mode
        orm_builder.orm().session().close()
        orm_builder.clear_database()

    try:
        orm_builder.create_db_schema(test)
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
    # setattr(base.config.application_config, 'models', src.config.app_config.models)
    setattr(base.config.application_config, 'models', _orm_models)
    load_orm(src.config.app_config.port)

    # PREPARE SEQUENCERS FIRST
    _seq_module = _get_sequnecer_model_module(_models_modules)
    if _seq_module:
        try:
            _seq_module.main()
        except sqlalchemy.exc.IntegrityError:
            orm_builder.orm().session().rollback()
            print('Sequencer already contains keys, and will not be inserted again, continuing')

    # PREPARE DATABASE
    for m in _models_modules:
        try:
            m.main()
        except AttributeError:
            print(m.__name__, "doesn't have to be prepared")

        except sqlalchemy.exc.IntegrityError:
            orm_builder.orm().session().rollback()
            print('Database {} already exists, you can recreate it or leave it this way'.format(args.database_name))
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

    with open(__db_config_file) as _db_cfg:
        try:
            db_config = json.load(_db_cfg)
        except json.JSONDecodeError:
            print('Can not load database configuration')
            sys.exit(exit_status.DATABASE_NOT_CONFIGURED)

    _models_modules = []
    _get_orm_models(_models_modules, src.config.app_config)

    _port = str(src.config.app_config.port)
    if _port not in db_config:
        print('Missing database configuration for port: {}'.format(_port))
        sys.exit(exit_status.DATABASE_NOT_CONFIGURED)

    # _db_config = db_config[_port]
    # db_type = _db_config['db_type']
    #
    # __db_url = make_database_url(db_type, _db_config['db_name'], _db_config['db_host'], _db_config['db_port'],
    #                              _db_config['db_user'], _db_config['db_password'],
    #                              _db_config['charset'] if 'charset' in _db_config else 'utf8')

    # orm_builder = base.common.orm.orm_builder(__db_url, base.common.orm.sql_base)
    orm_builder = init_orm()

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


def _add_blog():

    _update_path()
    try:
        import src.config.app_config
    except ImportError as e:
        print('Can not find application configuration')
        sys.exit(exit_status.MISSING_PROJECT_CONFIGURATION)

    if not hasattr(src.config.app_config, 'db_config'):
        print('Missing Database configuration in config file')
        sys.exit(exit_status.MISSING_DATABASE_CONFIGURATION)

    # check if config file has active models, and update models with blog models
    # check if models are presented if not copy them
    # create tables for blog (https://stackoverflow.com/questions/41030566/sqlalchemy-add-a-table-to-an-already-existing-database)
    #   orm has to bi initialized
    #   model_name.__table__.create(db_session.bind)
    # check if api exists, if not copy it from the repo
    # update app config with api paths

    print('blog added to the system')


def _add_component(parsed_args):

    if parsed_args.component not in available_BASE_components:
        print('''
        Component "{}" not recognized,
        please use 'db_init list' to see available components
        '''.format(parsed_args.component))
        sys.exit(exit_status.BASE_COMPONENT_NOT_EXISTS)

    if parsed_args.component == 'blog':
        _add_blog()


def _list_components(parsed_args):
    msg = '''
    available components: {}
    '''.format(''.join(['\n\t{}'.format(c) for c in available_BASE_components]))
    print(msg)


def execute_builder_cmd():

    parsed_args = pars_command_line_arguments()

    if parsed_args.cmd in ['init', 'i']:
        _build_project(parsed_args)

    if parsed_args.cmd in ['db_init', 'dbi']:
        _build_database(parsed_args)

    if parsed_args.cmd in ['db_show_create', 'dbs']:
        _show_create_table(parsed_args)

    if parsed_args.cmd in ['playground', 'p']:
        _create_playground(parsed_args)

    if parsed_args.cmd in ['add', 'a']:
        _add_component(parsed_args)

    if parsed_args.cmd in ['list', 'l']:
        _list_components(parsed_args)
