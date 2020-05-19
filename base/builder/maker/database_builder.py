import os
import sys
import json
import shutil
import importlib
import importlib.util
import sqlalchemy
import sqlalchemy.exc

from base.application.lookup import exit_status
from base.builder.maker.common import update_path
from base.builder.maker.common import get_install_directory
from base.builder.maker.common import get_orm_models
from base.common.orm import init_orm
from base.common.orm import make_database_url
from base.common.orm import make_database_url2
from base.config.settings import app
from base.config.settings import default_models
from base.config.settings import models_config_file
from base.config.settings import database_configuration_file


def _enable_database_in_config(config_file, args):

    # create models config file
    models_file = '{}/{}'.format(os.path.dirname(config_file), models_config_file)
    if not os.path.isfile(models_file):
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


def _configure_database(args, app_config, _db_config, test=False):

    __dest_dir = os.path.dirname(app_config.__file__)
    __db_config_file = '{}/{}'.format(__dest_dir, app_config.db_config)

    if not os.path.isfile(__db_config_file):
        print('Create database configuration for application port {}'.format(args.application_port))
    else:
        if not test:
            print('Update database configuration with application port {}'.format(args.application_port))

        from base.common.orm import load_database_configuration
        load_database_configuration(app_config, _db_config)

    if not test:
        __port = str(args.application_port)
        _db_config[__port] = {
            'db_name': args.database_name,
            'db_user': args.user_name,
            'db_password': args.password,
            'db_host': args.database_host,
            'db_type': args.database_type,
        }

        try:
            _db_config[__port]['db_port'] = args.database_port if args.database_port else \
                str(app['database_port'][0][args.database_type])
        except KeyError as e:
            print('Wrong database type configured: {}'.format(args.database_type))
            return False

        from src.config.app_config import read_only_ports

        if read_only_ports and len(read_only_ports):
            for port in read_only_ports:
                if str(port) not in _db_config:
                    _db_config[str(port)] = _db_config[__port].copy()
                    _db_config[str(port)]['db_user'] += "_readonly"

        with open(__db_config_file, 'w') as _db_cfg:
            _db_cfg.write(json.dumps(to_db_cfg_list(_db_config), ensure_ascii=False, sort_keys=True, indent=4))

    return True


# group by the same configuration, and add port to svc_port
def to_db_cfg_list(db_cfg_map):

    cvt={}
    for port in db_cfg_map:
        d = db_cfg_map[port]
        _key = "{}:{}:{}:{}:{}:{}".format(d['db_host'] if 'db_host' in d else '',
                                       d['db_name'] if 'db_name' in d else '',
                                       d['db_password'] if 'db_password' in d else '',
                                       d['db_port'] if 'db_port' in d else '',
                                       d['db_type'] if 'db_type' in d else '',
                                       d['db_user'] if 'db_user' in d else '')

        if _key not in cvt:
            cvt[_key] = {'ports': [int(port)],
                         'cfg': d.copy()}
        else:
            cvt[_key]['ports'].append(int(port))

    res = []
    for k in cvt:
        c = cvt[k]['cfg']
        c['svc_ports'] = sorted(cvt[k]['ports'])
        res.append(c)

    return res


def __db_is_configured(args, test):

    try:
        import src.config.app_config
    except ImportError as e:
        print('Can not find application configuration')
        return False, False

    if not test and not _enable_database_in_config(src.config.app_config.__file__, args):
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

    __port = str(src.config.app_config.port) if test else str(args.application_port)

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


def _create_database(db_name, db_type, db_config, test=False):

    from sqlalchemy import create_engine
    if db_type == 'sqlite':
        return True
    else:
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


def _copy_database_components(args, db_type, db_name, db_config):

    _site_dir = get_install_directory()
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
                    if db_type == 'sqlite':
                        _project_directory = os.getcwd()
                        _line = 'sqlalchemy.url = {}:///{}/{}.db\n'.format(db_type, _project_directory, db_name)
                    else:
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


def _get_sequencer_model_module(_models_modules):

    for m in _models_modules:
        if 'sequencer' in m.__name__:
            _models_modules.remove(m)
            return m


def build_database(args, test=False):

    update_path()

    db_config, db_type = __db_is_configured(args, test)
    if not db_config:
        sys.exit(exit_status.DATABASE_CONFIGURATION_ERROR)

    _database_name = 'test_{}'.format(db_config['db_name']) if test else db_config['db_name']
    __db_url = make_database_url(db_type, _database_name, db_config['db_host'], db_config['db_port'],
                                 db_config['db_user'], db_config['db_password'],
                                 db_config['charset'] if 'charset' in db_config else 'utf8')

    import base.common.orm
    if base.common.orm.orm is None:
        orm_builder = base.common.orm.orm_builder(__db_url, base.common.orm.sql_base)
        setattr(base.common.orm, 'orm', orm_builder.orm())
    else:
        orm_builder = base.common.orm.orm.orm_builder

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
    _orm_models = get_orm_models(_models_modules, src.config.app_config)

    if test:
        # teardown database in test mode
        orm_builder.orm().session().close()
        orm_builder.clear_database()

    try:
        orm_builder.create_db_schema(test)
    except sqlalchemy.exc.OperationalError:
        print('Database {} is missing, please create it'.format(args.database_name))
        sys.exit(exit_status.DATABASE_INITIALIZATION_ERROR)

    # LOAD ORM FOR SEQUENCERS IN MODELS
    from base.application.helpers.importer import load_orm
    import base.config.application_config
    setattr(base.config.application_config, 'models', _orm_models)
    load_orm(src.config.app_config.port)

    # PREPARE SEQUENCERS FIRST
    _seq_module = _get_sequencer_model_module(_models_modules)
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


def _database_is_configured():

    import src.config.app_config
    _models_file = '{}/{}'.format(os.path.dirname(src.config.app_config.__file__), models_config_file)
    if not os.path.isfile(_models_file) and not hasattr(src.config.app_config, 'models'):
        print('Missing models configuration')
        return False
    _alembic_dir = 'db'
    if not os.path.isdir(_alembic_dir):
        print('Missing alembic structure')
        return False
    _db_config_file = '{}/{}'.format(os.path.dirname(src.config.app_config.__file__), database_configuration_file)
    if not os.path.isfile(_db_config_file):
        print('Missing database configuration')
        return False

    return True


def _get_database_configuration():

    import src.config.app_config
    _db_config_file = '{}/{}'.format(os.path.dirname(src.config.app_config.__file__), database_configuration_file)
    with open(_db_config_file) as df:
        try:
            _db_config_all = json.load(df)

            if type(_db_config_all) == list:
                _new_config = {}
                for _db_config in _db_config_all:
                    for _port in _db_config['svc_ports']:
                        cfg = _db_config.copy()
                        del cfg['svc_ports']
                        print('CFG', cfg)
                        _new_config[str(_port)] = cfg
                _db_config_all = _new_config

            if src.config.app_config.port not in _db_config_all and \
                    str(src.config.app_config.port) not in _db_config_all:
                print('Configured port {} is not in database configuration'.format(src.config.app_config.port))
                return False

            _db_config = _db_config_all[src.config.app_config.port] if src.config.app_config.port in _db_config_all else \
                _db_config_all[str(src.config.app_config.port)]
        except Exception as e:
            print('Error load database configuration')
            return False

    return _db_config


def build_database_with_alembic(args):

    update_path()

    if not _database_is_configured():
        print('Database not configured')
        sys.exit(exit_status.DATABASE_NOT_CONFIGURED)

    db_config = _get_database_configuration()
    if not db_config:
        sys.exit(exit_status.DATABASE_CONFIGURATION_ERROR)

    if not _create_database(db_config['db_name'], db_config['db_type'], db_config, False):
        print('Database has not created')
        return

    orm_builder = init_orm()
    print('Database initialization finished')

    try:
        orm_builder.upgrade_db_schema()
    except sqlalchemy.exc.OperationalError:
        print('Database {} is missing, please create it'.format(args.database_name))
        sys.exit(exit_status.DATABASE_INITIALIZATION_ERROR)

    # PRESENT MODELS TO BASE
    import src.config.app_config
    _models_modules = []
    _orm_models = get_orm_models(_models_modules, src.config.app_config)

    # LOAD ORM FOR SEQUENCERS IN MODELS
    from base.application.helpers.importer import load_orm
    import base.config.application_config
    # setattr(base.config.application_config, 'models', src.config.app_config.models)
    setattr(base.config.application_config, 'models', _orm_models)
    load_orm(src.config.app_config.port)

    # PREPARE SEQUENCERS FIRST
    _seq_module = _get_sequencer_model_module(_models_modules)
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

