#!/usr/bin/env python3

import os
import sys
import json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from base_svc.comm import call
from base_api.users.user_register import location

data = {
    'username': 'user92',
    'password': '123'
}

svc_url = 'localhost'
svc_port = 8600

res, status = call(svc_url, svc_port, location, data, 'POST')
res = json.loads(res)
if status < 300:
    print(res['params']['token'])
else:
    print(res['message'])


