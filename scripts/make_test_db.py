#!/usr/bin/env python3

import os
import sys

usage = '''
{} source_db_name db_user db_password [dmp_path]
'''.format(sys.argv[0])

if len(sys.argv) < 4:
    print(usage)
    sys.exit(1)


dbm_file_path = os.getcwd()
if len(sys.argv) == 5:
    tmp_path = sys.argv[4]
    if not os.path.exists(tmp_path):
        print(tmp_path, "don't exists, please create desired directory")
        sys.exit(1)

    dbm_file_path = tmp_path

db_name = sys.argv[1]
db_user = sys.argv[2]
db_pwd = sys.argv[3]

dump_app = 'mysqldump'
dump_cmd = '{} -u{} -p{} -d {} > {}/test_{}'.format(
    dump_app, db_user, db_pwd, db_name, dbm_file_path, db_name
)

os.system(dump_cmd)
