# -*- coding: utf-8 -*-

from collections import namedtuple
DbConfig = namedtuple('DbConfig', 'db, host, user, passwd, charset')
db_config = DbConfig('test_db', 'localhost', 't_user', '123', 'utf8')
