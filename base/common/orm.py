import os
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from base.application.helpers.exceptions import UnknownDatabaseType


sql_base = declarative_base()


def make_database_url(db_type, name, host, port, username, password):

    if db_type == 'mysql':
        return 'mysql+mysqldb://{}:{}@{}:{}/{}'.format(username, password, host, port, name)
    if db_type == 'postgresql':
        return 'postgresql+psycopg2://{}:{}@{}:{}/{}'.format(username, password, host, port, name)
    if db_type == 'sqlite':
        return 'sqlite:///{}.db'.format(name)
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
            cls.__session = cls.__session_factory()
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

    def create_db_schema(self):
        self.__orm.base().metadata.create_all(self.__orm.engine())
        self.__orm.session().commit()

    def clear_database(self):
        if self.__orm.engine().name == 'sqlite':
            _db_name = self.__orm.db_url()[len('sqlite:///'):]
            os.remove(_db_name)
        else:
            __meta = sqlalchemy.MetaData(self.__orm.engine())
            __meta.reflect()
            __meta.drop_all()

    def orm(self):
        return self.__orm


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

