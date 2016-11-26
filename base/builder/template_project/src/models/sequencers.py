from sqlalchemy import Column, String, SmallInteger, Boolean, Index
import common.orm


class Sequencer(common.orm.sql_base):

    __tablename__ = 'sequencer'

    id = Column(String(2), primary_key=True)
    s_partition = Column(String(2), nullable=False)
    size = Column(SmallInteger, nullable=False)
    active_stage = Column(String(3), nullable=False)
    check_sum_size = Column(SmallInteger, nullable=False)
    name = Column(String(64), nullable=False, unique=True)
    type = Column(String(16), nullable=False)
    s_table = Column(String(64), nullable=False, unique=True)
    ordered = Column(Boolean, nullable=False, default=False)

    def __init__(self, _id, s_partition, active_stage, size, check_sum_size, name, _type, s_table, ordered=False):

        self.id = _id
        self.s_partition = s_partition
        self.active_stage = active_stage
        self.size = size
        self.check_sum_size = check_sum_size
        self.name = name
        self.type = _type
        self.s_table = s_table
        self.ordered = ordered


class s_users(common.orm.sql_base):

    __tablename__ = 's_users'

    id = Column(String(10), primary_key=True)
    active_stage = Column(String(3), index=True, nullable=False)

    # __table_args__ = (Index('_s_users_idx0', 'active_stage'),)

    def __init__(self, _id, active_stage):

        self.id = _id
        self.active_stage = active_stage


class s_session_token(common.orm.sql_base):

    __tablename__ = 's_session_token'

    id = Column(String(64), primary_key=True)
    active_stage = Column(String(3), index=True, nullable=False)

    # __table_args__ = (Index('_s_session_token_idx0', 'active_stage'),)

    def __init__(self, _id, active_stage):

        self.id = _id
        self.active_stage = active_stage


class s_hash_2_params(common.orm.sql_base):

    __tablename__ = 's_hash_2_params'

    id = Column(String(64), primary_key=True)
    active_stage = Column(String(3), index=True, nullable=False)

    # __table_args__ = (Index('_s_hash_2_params_idx0', 'active_stage'),)

    def __init__(self, _id, active_stage):

        self.id = _id
        self.active_stage = active_stage


def main():

    _session = common.orm.orm.session()

    for _s in [
        ('u', '00', '000', 4, 0, 'users', 'STR', 's_users', False),
        ('s', '00', '000', 58, 0, 'session_token', 'STR', 's_session_token', False),
        ('h', '00', '000', 58, 0, 'hash_2_params', 'STR', 's_hash_2_params ', False)]:
        _seq = Sequencer(*_s)

        _session.add(_seq)

    _session.commit()

if __name__ == '__main__':

    main()

