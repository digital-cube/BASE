# -*- coding: utf-8 -*-

import logging
from logging.handlers import TimedRotatingFileHandler
from base_config.settings import LOG_DIR

support_mail = 'support@support.com'

log_filename = "{}/base.log".format(LOG_DIR)
log_handler = TimedRotatingFileHandler(log_filename, when="midnight")
log_formatter = logging.Formatter(
        '%(asctime)-6s %(name)s %(module)s %(funcName)s %(lineno)d - %(levelname)s %(message)s')
log_handler.setFormatter(log_formatter)

log = logging.getLogger('DGTL')
log.propagate = False
log.addHandler(log_handler)
log.setLevel(logging.DEBUG)

log_a_filename = "{}/base_action.log".format(LOG_DIR)
log_a_handler = TimedRotatingFileHandler(log_a_filename, when="midnight")
log_a_formatter = logging.Formatter(
        '%(asctime)-6s %(name)s %(module)s %(funcName)s %(lineno)d - %(levelname)s %(message)s')
log_a_handler.setFormatter(log_a_formatter)

log_a = logging.getLogger('ACTION')
log_a.propagate = False
log_a.addHandler(log_a_handler)
log_a.setLevel(logging.DEBUG)


