from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, ForeignKey
import datetime
import common.orm


class Options(common.orm.sql_base):

    __tablename__ = 'options'

    id = Column(Integer, primary_key=True)
    key = Column(String(64), index=True, nullable=False)
    value = Column(String(64), nullable=False)

    def __init__(self, key, value):

        self.key = key
        self.value = value


class Hash2Params(common.orm.sql_base):

    __tablename__ = 'hash_2_params'

    id = Column(Integer, primary_key=True, autoincrement=True)
    hash = Column(String(64), index=True, nullable=False, unique=True)
    created = Column(DateTime, nullable=False, default=datetime.datetime.now())
    time_to_live = Column(Integer)
    expire_after_first_access = Column(Boolean, nullable=False, default=False)
    last_access = Column(DateTime, nullable=False, default=datetime.datetime.now())
    data = Column(Text, nullable=False)

    def __init__(self, _hash, data, time_to_live=None, expire_after_first_access=False):

        self.hash = _hash
        self.data = data
        if time_to_live is not None:
            self.time_to_live = time_to_live
        if expire_after_first_access:
            self.expire_after_first_access = expire_after_first_access

    def set_last_access(self, access_datetime):
        self.last_access = access_datetime


class Hash2ParamsHistory(common.orm.sql_base):

    __tablename__ = 'hash_2_params_history_log'

    id = Column(Integer, primary_key=True, autoincrement=True)
    id_hash_2_params = Column(Integer, ForeignKey('hash_2_params.id'), nullable=False)
    created = Column(DateTime, nullable=False, default=datetime.datetime.now())
    data = Column(Text, nullable=False)

    def __init__(self, id_hash, data):

        self.hash = hash
        self.data = data


def main():

    _session = common.orm.orm.session()

    import src.config.app_config
    _o = Options('version', src.config.app_config.app_version)
    _session.add(_o)
    _session.commit()


if __name__ == '__main__':

    main()
