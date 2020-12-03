# coding= utf-8
import os
import datetime
import decimal
import sqlalchemy

from sqlalchemy import create_engine, inspect, TIMESTAMP, Column, Numeric
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine.url import URL
from sqlalchemy.dialects.postgresql import UUID

sql_base = declarative_base()
_orm = {}

current_file_folder = os.path.dirname(os.path.realpath(__file__))


def make_database_url(db_config, charset='utf8'):
    db_type = db_config['type']
    name = db_config['database']
    host = db_config['host']
    port = db_config['port']
    username = db_config['username']
    password = db_config['password']

    if db_type == 'mysql':
        return URL(drivername='mysql+mysqldb', username=username, password=password, host=host, port=port,
                   database=name, query={'charset': charset})
    if db_type in ('postgresql', 'postgres'):
        return URL(drivername='postgresql+psycopg2', username=username, password=password, host=host, port=port,
                   database=name, query={'client_encoding': charset})
    if db_type == 'sqlite':
        return URL(drivername='sqlite', database='{}.db'.format(name))
    else:
        raise NameError("Unknown database type: {}".format(db_type))


class Orm(object):
    __instance = {}

    def __new__(cls, sql_address, orm_base, **kwargs):
        if not Orm.__instance or sql_address not in Orm.__instance:
            Orm.__instance[sql_address] = object.__new__(cls)

            Orm.__instance[sql_address].__db_url = sql_address
            Orm.__instance[sql_address].__engine = create_engine(Orm.__instance[sql_address].__db_url, echo=False,
                                                                 **kwargs)
            Orm.__instance[sql_address].__session_factory = sessionmaker(
                bind=Orm.__instance[sql_address].__engine)  # , autoflush=False, autocommit=False)
            Orm.__instance[sql_address].__scoped_session = scoped_session(Orm.__instance[sql_address].__session_factory)
            Orm.__instance[sql_address].__session = Orm.__instance[sql_address].__scoped_session()
            Orm.__instance[sql_address].__base = orm_base

        return Orm.__instance[sql_address]

    def base(self):
        return self.__base

    def engine(self):
        return self.__engine

    def session(self):
        __session_factory = sessionmaker(bind=self.__engine)
        __scoped_session = scoped_session(__session_factory)
        return __scoped_session()


class orm_builder(object):

    def __init__(self, sql_address, orm_base, **kwargs):
        self.__orm = Orm(sql_address, orm_base, **kwargs)
        setattr(self.__orm, 'orm_build', self)

    def create_db_schema(self):
        self.__orm.base().metadata.create_all(self.__orm.engine())
        r = self.__orm.session().commit()

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


def init_orm(db_config):
    __db_url = make_database_url(db_config, 'utf8')

    return orm_builder(__db_url, sql_base)


class _BaseSql():

    def __init__(self, **kwa):

        import uuid

        self.id = str(uuid.uuid4()) if 'id' not in kwa else kwa['id']

        for column in inspect(self).attrs:
            if column.key == 'id':
                continue

            if column.key in kwa:
                self.__setattr__(column.key, kwa[column.key])

    def update(self, source):

        updated = []

        for column in inspect(self).attrs:
            if column.key == 'id':
                continue

            if column.key in source:
                # if column.key in source.__dict__:

                if type(self.__dict__[column.key])==dict:
                    if self.__dict__[column.key] != source[column.key]:
                        updated.append(column.key)

                else:
                    if str(self.__dict__[column.key]) != str(source[column.key]):
                        updated.append(column.key)

                self.__setattr__(column.key, source[column.key])

        return updated

    def keys(self, skip: set = {}):
        res = []
        for key in self.__dict__:
            if key == '_sa_instance_state' or key in skip:
                continue
            res.append(key)

        return res

    def serialize(self, keys=None, forbidden=[]):

        # print("serialize",self.id)
        def _serialize(s):
            # print(type(s), s)

            if type(s) in (Numeric, decimal.Decimal):
                return float(s)
            elif type(s) in (int, float, str, dict, None):
                return s
            elif type(s) == bool:
                return True if s in (True, "True", 'true', 'yes', 'Yes', '1') else False

            return str(s) if s is not None else None

        result = {}

        if self.id:  # TODO: DON'T REMOVE THIS
            pass  # hack for __dict__, if you remove this code, __dict__ will not be initialized in runtime

        # ukoliko su navedeni kljucevi, zgodno bi bilo ubaciti ih u serializaciju po redosledu
        if keys:
            for key in keys:
                if key in self.__dict__ and key not in forbidden:
                    result[key] = _serialize(self.__dict__[key])

        else:
            for key in self.__dict__:
                if key == '_sa_instance_state':
                    continue

                if key in forbidden:
                    continue

                if not keys or key in keys:
                    result[key] = _serialize(self.__dict__[key])

        return result


def activate_orm(db_config: dict):
    global _orm
    global sql_base

    _db_url = make_database_url(db_config, 'utf8')

    _orm[db_config['database']] = Orm(_db_url, sql_base)


class BaseSql(_BaseSql):
    id = Column(UUID, primary_key=True)
    created = Column(TIMESTAMP, index=True)

    def __init__(self, **kwargs):
        n = datetime.datetime.now()
        self.created = datetime.datetime(n.year, n.month, n.day, n.hour, n.minute, n.second)

        super().__init__(**kwargs)
