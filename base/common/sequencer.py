# -*- coding: utf-8 -*-

import string
import random
import base.common.orm
import sqlalchemy.exc
from base.application.helpers.exceptions import ToManyAttemptsException
from base.application.helpers.exceptions import SequencerTypeError


class SequencerFactory:
    """
    SequencerFactory - instantiated only once, as a singleton
    """

    _reserved_table_name = 'normalseq'

    def __init__(self, db, seq_orm_table_model=None):

        self.max_attempts = 100

        self.t_str = list(string.digits) * 4 + \
                     list(string.ascii_lowercase) * 3 + \
                     list(string.ascii_uppercase) * 3
        self.n_str = 10 + 26 + 26

        self.t_i_str = list(string.digits) * 4 + \
                      list(string.ascii_uppercase) * 3
        self.n_i_str = 10 + 26

        self.t_num = list(string.digits) * 4
        self.n_num = 10

        self.t_visual = [i for i in list(string.digits) if i not in ['1', '8', '0']] * 3 + \
                        [i for i in list(string.ascii_uppercase) if i not in ['O', 'B', 'I', 'J', 'L', 'Q']]
        self.n_visual = (10 - 3) + (26 - 6)

        self.prime_numbers = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47,
                              53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131]

        self.db = db
        self.seq_orm_table_model = seq_orm_table_model
        self.s_table = {}
        self.load_s_table()

    def load_s_table(self):

        import base.config.application_config
        import base.common.orm
        Sequencer = self.seq_orm_table_model if self.seq_orm_table_model is not None \
            else base.config.application_config.orm_models['sequencer']

        with base.common.orm.orm_session() as _session:
            
            _q = _session.query(Sequencer)
            for s in _q.all():
                self.s_table[s.id] = {
                    'table_id': s.id,
                    'partition_id': s.s_partition,
                    'active_stage': s.active_stage,
                    'size': s.size,
                    'check_sum_size': s.check_sum_size,
                    'name': s.name,
                    'type': s.type,
                    's_table': s.s_table,
                    'ordered': bool(s.ordered)
                }

    def create_random_id(self, size, id_type):

        if id_type == 'STR':
            random.shuffle(self.t_str)
            return ''.join(self.t_str[:size])

        return '_' * size

    def checksum(self, _id, size, id_type):

        if size == 0:
            return ''

        x = 0
        for c in range(0, len(_id)):
            x += self.prime_numbers[c] * ord(_id[c])

        return '2' * size

    def check_db(self):
        """Check db connection"""

        return True

    def new(self, table_id, session=None, commit=False):

        from base.common.utils import log

        if table_id not in self.s_table:
            log.critical('Wrong sequencer table id provided {}'.format(table_id))
            return False

        import src.models.sequencers
        if not hasattr(src.models.sequencers, self.s_table[table_id]['s_table']):
            log.critical('Missing {} model definition in {}'.format(
                self.s_table[table_id]['s_table'], src.models.sequencers.__file__))
            return False

        _orm_model =  getattr(src.models.sequencers, self.s_table[table_id]['s_table'])

        id_prefix = "{}{}{}".format(self.s_table[table_id]['table_id'],
                                    self.s_table[table_id]['partition_id'],
                                    self.s_table[table_id]['active_stage'])

        import base.common.orm
        with base.common.orm.orm_session() as _session:
            __session = session if session else _session
            attempt = 1
            while True:

                if self.s_table[table_id]['ordered']:
                    log.warning('Orderd table')
                    return False

                else:
                    _id = self.create_random_id(self.s_table[table_id]['size'], self.s_table[table_id]['type'])

                _s_id = id_prefix + _id
                _s_id += self.checksum(_s_id, self.s_table[table_id]['check_sum_size'], self.s_table[table_id]['type'])

                _s = _orm_model(_s_id, self.s_table[table_id]['active_stage'])
                __session.add(_s)

                if commit:
                    try:
                        __session.commit()
                    except sqlalchemy.exc.IntegrityError as e:
                        __session.rollback()
                        if attempt >= self.max_attempts:
                            log.critical('To many attempts to create id for {} table'.format(
                                self.s_table[table_id]['s_table']))
                            raise ToManyAttemptsException('creating id for {} table'.format(
                                self.s_table[table_id]['s_table']))
                        attempt += 1
                        continue

                break

        return _s_id

    def get_sequence(self, sequence_id, sequence):

        from base.common.utils import log
        import base.common.orm

        if sequence_id not in self.s_table:
            log.critical('Sequence id {} is not in the system'.format(sequence_id))
            return False

        db_sequence = self.s_table[sequence_id]

        db_sequence_lenght = len(sequence_id) + \
                          len(db_sequence['partition_id']) + \
                          len(db_sequence['active_stage']) +\
                          int(db_sequence['size']) + \
                          int(db_sequence['check_sum_size'])

        import src.models.sequencers
        _sequencer_model = getattr(src.models.sequencers, db_sequence['s_table'], None)
        if not _sequencer_model:
            log.critical('Missing sequencer {} table model in {}'.format(
                db_sequence['s_table'], src.models.sequencers.__file__ ))
            return False

        with base.common.orm.orm_session() as _session:
            _q = _session.query(_sequencer_model).filter(_sequencer_model.id==sequence).all()

            if len(_q) != 1:
                log.critical('Sequence id {} is not in {} table'.format(sequence_id, db_sequence['s_table']))
                return False

        return True


_sequencer = None


def sequencer(db=None, seq_orm_table_model=None):
    """Sequencer singleton getter"""

    global _sequencer
    if not _sequencer or not _sequencer.check_db():
        if db:
            _sequencer = SequencerFactory(db, seq_orm_table_model)
        else:
            _sequencer = SequencerFactory(base.common.orm.orm, seq_orm_table_model)

    return _sequencer


def sid(s_id, model_table=SequencerFactory._reserved_table_name):
    """Return sequencer type with param 'model_table' which is used for retrieving table
    row with s_id as id. 'normalseq' is the reserve word, do not create table
    with id as the sequencer type and 'normalseq' as the name"""

    if ':' in model_table:
        raise SequencerTypeError('mode parameter can not contain the colon sign')

    return 'sequencer:{}:{}'.format(model_table, s_id)


