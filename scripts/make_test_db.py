#!/usr/bin/env python3

import os
import sys

usage = '''
{} source_db_name db_user db_password [dmp_path] [-r required tables list]
'''.format(sys.argv[0])

if len(sys.argv) < 4:
    print(usage)
    sys.exit(1)

dbm_file_path = os.getcwd()
required_tables = None
if len(sys.argv) > 5:

    if '-r' in sys.argv:
        i = sys.argv.index('-r')
        tmp_required_list = sys.argv[i+1:]
        if tmp_required_list:
            required_tables = ' '.join(tmp_required_list)

    if sys.argv[4] != '-r':
        tmp_path = sys.argv[4]
        if not os.path.exists(tmp_path):
            print(tmp_path, "don't exists, please create desired directory")
            sys.exit(1)

        dbm_file_path = tmp_path

db_name = sys.argv[1]
db_user = sys.argv[2]
db_pwd = sys.argv[3]

db_app = 'mysql'
dump_app = 'mysqldump'

dump_cmd = '{} -u{} -p{} -d {} > {}/test_{}.dmp'.format(
    dump_app, db_user, db_pwd, db_name, dbm_file_path, db_name
)
# crate sql schema dump for test
os.system(dump_cmd)

if required_tables:
    print('FUCK REQ')
    dump_required_tables_cmd = '{} -u{} -p{} {} -t {} >> {}/test_{}.dmp'.format(
        dump_app, db_user, db_pwd, db_name, required_tables, dbm_file_path, db_name
    )
    print(dump_required_tables_cmd)
    # add required tables to dump
    os.system(dump_required_tables_cmd)

destroy_test_db_cmd = "{} -u{} -p{} -e 'drop database if exists test_{}'".format(db_app, db_user, db_pwd, db_name)
create_test_db_cmd = "{} -u{} -p{} -e 'create database test_{}'".format(db_app, db_user, db_pwd, db_name)
# destroy test db if exists
os.system(destroy_test_db_cmd)
# create test databse
os.system(create_test_db_cmd)

fill_test_db_cmd = "{} -u{} -p{} test_{} < {}/test_{}.dmp".format(
    db_app, db_user, db_pwd, db_name, dbm_file_path, db_name
)

# create test db tables
os.system(fill_test_db_cmd)
