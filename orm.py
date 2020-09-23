# coding= utf-8
import os
import json
import contextlib

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

from sqlalchemy import Column, DateTime
import datetime

from sqlalchemy.engine.url import URL
from sqlalchemy import inspect

sql_base = declarative_base()
_orm = {}
import sqlalchemy

current_file_folder = os.path.dirname(os.path.realpath(__file__))


def make_database_url(db_config, charset='utf8'):
    """Create database url"""

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
        self.__orm.session().commit()

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


class BaseSql():
    created = Column(DateTime, index=True)
    #
    # @staticmethod
    # def _build(model, data, mandatory_fields, optional_fields, relations):
    #
    #     mfkeys = set(mandatory_fields.keys()) if mandatory_fields else {}
    #     okeys = set(optional_fields.keys()) if optional_fields else {}
    #
    #     if mfkeys.intersection((okeys)):
    #         raise NameError("keys {mfkeys.intersection((okeys))} can't be mandatory and optional")
    #
    #     # add_fk_relations = {}
    #     # to_remove = []
    #     for f in mandatory_fields:
    #         if f not in data:
    #             raise NameError(f"mandatory field {f} not presented in input")
    #         # if f in relations:
    #     #         to_remove.append(f)
    #     #         add_fk_relations[f] = data[f]
    #     #
    #     # try:
    #
    #     for f in data:
    #         if f not in mandatory_fields and f not in optional_fields:
    #             raise NameError(f"field {f} is not valid field for constructing Product")
    #
    #     #         if f in relations:
    #     #             to_remove.append(f)
    #     #             if f in data:
    #     #                 add_fk_relations[f] = data[f]
    #     # except Exception as e:
    #     #     print('pass')
    #     #
    #     # for k in to_remove:
    #     #     del data[k]
    #
    #     m = model(**data)
    #     # for id_fk in add_fk_relations:
    #     #     setattr(m, id_fk, add_fk_relations[id_fk])
    #
    #     return m

    def __init__(self, **kwa):

        import uuid

        self.created = datetime.datetime.now()

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
                if self.__dict__[column.key] != source[column.key]:
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

    def serialize(self, keys=None):

        def _serialize(s):
            if type(s) in (int, float, str):
                return s
            return str(s) if s is not None else None

        result = {}

        for key in self.__dict__:
            if key == '_sa_instance_state':
                continue

            if not keys or key in keys:
                result[key] = _serialize(self.__dict__[key])

        return result


def activate_orm(db_config):
    global _orm
    global sql_base

    _db_url = make_database_url(db_config, 'utf8')

    _orm[db_config['database']] = Orm(_db_url, sql_base)

# izmesteno je u same mikro servise / orm.py da bi importovao konkretnu konfiguraciju kao i module sa modelima

#
# @contextlib.contextmanager
# def orm_session():
#     if not base_orm._orm:
#
#         base_orm.activate_orm(db_config)
#
#     _session = base_orm._orm.session()
#     try:
#         yield _session
#     except:
#         _session.rollback()
#         _session.close()
#         raise
#     finally:
#         _session.close()
