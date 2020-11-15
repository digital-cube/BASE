#!/usr/bin/python3
"""
Send mail runner
"""

import os
import sys
import time
port = 8801 if len(sys.argv) == 1 else int(sys.argv[1])
while True:
    os.system('python3 send_mail.py {} -s'.format(port))
    time.sleep(1)
