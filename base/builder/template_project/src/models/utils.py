from sqlalchemy import Column, String, Integer, SmallInteger, Boolean
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

    def __init__(self, s_partition, size, active_stage, check_sum_size, name, type, s_table):

        self.s_partition = s_partition
        self.size = size
        self.active_stage = active_stage
        self.check_sum_size = check_sum_size
        self.name = name
        self.type = type


class Options(common.orm.sql_base):

    __tablename__ = 'options'

    id = Column(Integer, primary_key=True)
    key = Column(String(64), nullable=False)
    value = Column(String(64), nullable=False)

    def __init__(self, key, value):

        self.key = key
        self.value = value
