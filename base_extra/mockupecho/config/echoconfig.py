
from collections import namedtuple
DbConfig = namedtuple('DbConfig', 'db, host, user, passwd, charset')
db_config = DbConfig('db_name', 'localhost', 'db_user', 'db_pass', 'utf8')
