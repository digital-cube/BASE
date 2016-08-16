# -*- coding: utf-8 -*-

import string
import random
from base_common import dbacommon
from base_common.dbaexc import ToManyAttemptsException
from MySQLdb import IntegrityError


class SequencerFactory:
    """
    SequencerFactory
    """

    def getDB(self):
        return self.db

    # def __init__(self, host, user, passwd, db, charset):
    def __init__(self, db):

        self.max_attempts = 100

        self.t_str = list(string.digits)*4 + \
                     list(string.ascii_lowercase)*3 +\
                     list(string.ascii_uppercase)*3
        self.n_str = 10+26+26

        self.t_istr = list(string.digits)*4 +\
                      list(string.ascii_uppercase)*3
        self.n_istr = 10+26

        self.t_num = list(string.digits)*4
        self.n_num = 10

        self.t_visual = [ i for i in list(string.digits) if i not in ['1','8','0'] ]*3 + \
                        [ i for i in list(string.ascii_uppercase) if i not in ['O', 'B', 'I', 'J', 'L', 'Q']]
        self.n_visual = (10-3)+(26-6)

        self.prime_numbers = [ 2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47,
                               53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131 ]

        self.db = db
        self.s_table = {}
        self.load_s_table()

    def load_s_table(self):

        c = self.db.cursor()
        c.execute("select id,s_partition,active_stage,size,check_sum_size,name,type,s_table,ordered from sequencers")
        for s in c.fetchall():
            self.s_table[ s['id'] ] = {
                'table_id': s['id'],
                'partition_id': s['s_partition'],
                'active_stage': s['active_stage'],
                'size': s['size'],
                'check_sum_size': s['check_sum_size'],
                'name': s['name'],
                'type': s['type'],
                's_table': s['s_table'],
                'ordered': bool(s['ordered'])
            }

    def create_random_id(self, size, id_type):

        if id_type == 'STR':
            random.shuffle(self.t_str)
            return ''.join(self.t_str[:size])

        return '_'*size

    def checksum(self, id, size, id_type):

        if size == 0:
            return ''

        x = 0
        for c in range(0,len(id)):
            x += self.prime_numbers[c]*ord(id[c])

        return '2'*size

    def check_db(self):

        dbc = self.db.cursor()
        import MySQLdb
        try:
            dbc.execute('select 1')
        except MySQLdb.OperationalError as e:
            return False

        return True

    def new(self, table_id, commit=True):

        if table_id not in self.s_table:
            return False

        id_prefix = "{}{}{}".format(self.s_table[table_id]['table_id'],
                             self.s_table[table_id]['partition_id'],
                             self.s_table[table_id]['active_stage'])

        attempt=1
        while True:

            if self.s_table[table_id]['ordered']:
                return False

            else:
                _id = self.create_random_id( self.s_table[table_id]['size'], self.s_table[table_id]['type'] )

            id = id_prefix + _id
            id += self.checksum(id, self.s_table[table_id]['check_sum_size'], self.s_table[table_id]['type'])

            try:
                n = self.db.cursor()
                n.execute("insert into {} (id,active_stage) values ('{}','{}')".format(
                        self.s_table[table_id]['s_table'],
                        id,
                        self.s_table[table_id]['active_stage']))
            except IntegrityError as e:
                if attempt>=self.max_attempts:
                    raise ToManyAttemptsException('creating id for {} table'.format(self.s_table[table_id]['s_table']))

                attempt+=1
                continue

            if commit:
                self.db.commit()
            break

        return id


_sequencer = None


def sequencer(db = None):

    global _sequencer
    if not _sequencer or not _sequencer.check_db():
        if db:
            _sequencer = SequencerFactory(db)
        else:
            _sequencer = SequencerFactory(dbacommon.get_db())

    return _sequencer


