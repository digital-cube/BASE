#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from logging.handlers import TimedRotatingFileHandler

log_filename = "/var/log/base/send_mail.log"
log_handler = TimedRotatingFileHandler(log_filename, when="midnight")
log_formatter = logging.Formatter(
    '%(asctime)-6s %(name)s %(module)s %(funcName)s %(lineno)d - %(levelname)s %(message)s')
log_handler.setFormatter(log_formatter)

log = logging.getLogger('DGTL')
log.propagate = False
log.addHandler(log_handler)
log.setLevel(logging.DEBUG)

db_host = 'localhost'
db_user = 'avuser'
db_passwd = '123'
db_name = 'avalon'  # Promenjeno za potrebe TESTA
db_charset = 'utf8'

sg_key = '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'

REDIS_SERVER = 'localhost'
REDIS_PORT = 6379
