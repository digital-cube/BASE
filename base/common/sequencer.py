# -*- coding: utf-8 -*-

import string
import random
import common.orm
import sqlalchemy.exc
from src.models.sequencers import Sequencer
from application.helpers.exceptions import ToManyAttemptsException


class SequencerFactory:
    """
    SequencerFactory
    """

    def __init__(self, db):

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
        self.s_table = {}
        self.load_s_table()

    def load_s_table(self):

        _q = self.db.session().query(Sequencer)
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
                'ordered': bool(s.ordered),
                'orm_model': s.s_table
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

    def new(self, table_id, commit=True):

        if table_id not in self.s_table:
            return False

        import src.models.sequencers
        if not hasattr(src.models.sequencers, self.s_table[table_id]['orm_model']):
            return False

        _orm_model =  getattr(src.models.sequencers, self.s_table[table_id]['orm_model'])

        id_prefix = "{}{}{}".format(self.s_table[table_id]['table_id'],
                                    self.s_table[table_id]['partition_id'],
                                    self.s_table[table_id]['active_stage'])

        attempt = 1
        while True:

            if self.s_table[table_id]['ordered']:
                return False

            else:
                _id = self.create_random_id(self.s_table[table_id]['size'], self.s_table[table_id]['type'])

            _s_id = id_prefix + _id
            _s_id += self.checksum(_s_id, self.s_table[table_id]['check_sum_size'], self.s_table[table_id]['type'])

            _s = _orm_model(_s_id, self.s_table[table_id]['active_stage'])
            self.db.session().add(_s)

            if commit:
                try:
                    self.db.session().commit()
                except sqlalchemy.exc.IntegrityError as e:
                    self.db.session().rollback()
                    if attempt >= self.max_attempts:
                        raise ToManyAttemptsException('creating id for {} table'.format(
                            self.s_table[table_id]['s_table']))
                    attempt += 1
                    continue

            break

        return _s_id


_sequencer = None


def sequencer(db=None):
    global _sequencer
    if not _sequencer or not _sequencer.check_db():
        if db:
            _sequencer = SequencerFactory(db)
        else:
            _sequencer = SequencerFactory(common.orm.orm)

    return _sequencer

