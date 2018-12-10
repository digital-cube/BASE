import os
import sys
import json
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine.url import URL
from base.application.lookup import exit_status
from base.application.helpers.exceptions import UnknownDatabaseType


sql_base = declarative_base()


def make_database_url(db_type, name, host, port, username, password, charset='utf8'):
    """Create database url"""

    if db_type == 'mysql':
        return URL(drivername='mysql+mysqldb', username=username, password=password, host=host, port=port, database=name, query={'charset': charset})
    if db_type == 'postgresql':
        return URL(drivername='postgresql+psycopg2', username=username, password=password, host=host, port=port, database=name, query={'client_encoding': charset})
    if db_type == 'sqlite':
        return URL(drivername='sqlite', database='{}.db'.format(name))
    else:
        raise UnknownDatabaseType("Unknown database type: {}".format(db_type))


def make_database_url2(db_type, host, port, username, password, charset='utf8'):
    """Create url without the database name to be able to check if the database exists.
    Postgresql url require database template1 as a name to be able to work"""

    if db_type == 'mysql':
        return URL(drivername='mysql+mysqldb', username=username, password=password, host=host, port=port, query={'charset': charset})
    if db_type == 'postgresql':
        return URL(drivername='postgresql+psycopg2', username=username, password=password, host=host, port=port, database='template1', query={'client_encoding': charset})
    if db_type == 'sqlite':
        return URL(drivername='sqlite')
    else:
        raise UnknownDatabaseType("Unknown database type: {}".format(db_type))


class _orm(object):

    __instance = None

    def __new__(cls, sql_address, orm_base):

        if _orm.__instance is None:
            _orm.__instance = object.__new__(cls)
            cls.__db_url = sql_address
            cls.__engine = create_engine(cls.__db_url, echo=False)
            cls.__session_factory = sessionmaker(bind=cls.__engine)
            cls.__scoped_session = scoped_session(cls.__session_factory)
            cls.__session = cls.__scoped_session()
            cls.__base = orm_base

        return _orm.__instance

    def session(self):
        return self.__session

    def engine(self):
        return self.__engine

    def db_url(self):
        return self.__db_url

    def base(self):
        return self.__base


class orm_builder(object):

    def __init__(self, sql_address, orm_base):
        self.__orm = _orm(sql_address, orm_base)

    def create_db_schema(self, test=False):
        """In test mode use sqlalchemy method, in other cases use alembic"""

        if test:
            self.__orm.base().metadata.create_all(self.__orm.engine())
            self.__orm.session().commit()
            return

        # alembic create all tables;
        from alembic.config import Config
        from alembic import command
        os.chdir('db')
        alembic_cfg = Config('alembic.ini')

        first_revision = command.show(alembic_cfg, "head")
        if first_revision is None:
            command.revision(alembic_cfg, autogenerate=True, message='initial')
        command.upgrade(alembic_cfg, "head")
        os.chdir('..')

    def upgrade_db_schema(self):
        """Generate database when alembic config is present"""

        # alembic create all tables;
        from alembic.config import Config
        from alembic import command
        os.chdir('db')
        alembic_cfg = Config('alembic.ini')
        command.upgrade(alembic_cfg, "head")
        os.chdir('..')

    def clear_database(self):
        if self.__orm.engine().name == 'sqlite':
            try:
                _db_name = self.__orm.db_url()[len('sqlite:///'):]
            except:
                _db_name = self.__orm.db_url().database

            os.remove(_db_name)
        else:
            __meta = sqlalchemy.MetaData(self.__orm.engine())
            __meta.reflect()
            __meta.drop_all()

    def orm(self):
        return self.__orm

    def add_blog(self):
        from alembic.config import Config
        from alembic import command
        os.chdir('db')
        alembic_cfg = Config('alembic.ini')

        command.revision(alembic_cfg, autogenerate=True, message='blog')
        command.upgrade(alembic_cfg, "head")
        os.chdir('..')


orm = None


def activate_orm(db_url):

    global orm
    global sql_base
    orm = _orm(db_url, sql_base)


def get_orm_model(model_name):

    global orm
    import base.config.application_config
    OrmModel = base.config.application_config.orm_models[model_name]
    # _session = base.common.orm.orm.session()
    _session = orm.session()

    return OrmModel, _session

def commit():
    global orm

    if not orm:
        raise NameError("DB Error: orm not initialised")

    _session = orm.session()
    try:
        _session.commit()
    except Exception as e:
        _session.rollback()

        import base.config.application_config as a_cfg
        if a_cfg.debug:
            raise NameError("DB Error: {}".format(e))
        else:
            raise NameError("DB Error")


def load_database_configuration(app_config, _db_config):

    _dir = os.path.dirname(app_config.__file__)
    _db_file = '{}/{}'.format(_dir, app_config.db_config)

    if not os.path.isfile(_db_file):
        return False

    _db_conf = {}
    with open(_db_file) as _db_cfg:
        try:
            _db_conf = json.load(_db_cfg)
        except json.JSONDecodeError:
            return False

    if type(_db_conf) == dict:
        for _k in _db_conf:
            _db_config[_k] = _db_conf[_k]

    elif type(_db_conf) == list:
        for pcfg in _db_conf:
            for _k in pcfg['svc_ports']:
                c = pcfg.copy()
                del c['svc_ports']
                _db_config[str(_k)] = c

    return True


def init_orm():

    import src.config.app_config

    __dest_dir = os.path.dirname(src.config.app_config.__file__)
    __db_config_file = '{}/{}'.format(__dest_dir, src.config.app_config.db_config)

    db_config = {}
    load_database_configuration(src.config.app_config, db_config)

    _port = str(src.config.app_config.port)

    _db_config = db_config[_port]
    db_type = _db_config['db_type']

    __db_url = make_database_url(db_type, _db_config['db_name'], _db_config['db_host'], _db_config['db_port'],
                                 _db_config['db_user'], _db_config['db_password'],
                                 _db_config['charset'] if 'charset' in _db_config else 'utf8')

    return orm_builder(__db_url, sql_base)

