#!/usr/bin/env python3

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import base_common.dbatests

usage = """
{} svc_port [usename and password]
""".format(sys.argv[0])

if len(sys.argv) < 2 or \
        (len(sys.argv) > 2 and len(sys.argv) != 4):
    print(usage)
    sys.exit(1)

# data = {
#     'username': 'user92',
#     'password': '123'
# }

svc_url = 'localhost'
svc_port = sys.argv[1]

if len(sys.argv) == 2:
    res, status = base_common.dbatests.test_authorize(svc_url, svc_port)
else:
    username = sys.argv[2]
    password = sys.argv[3]
    res, status = base_common.dbatests.test_authorize(svc_url, svc_port, username=username, password=password)

print(status,'\t', res)
