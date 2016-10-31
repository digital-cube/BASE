# coding= utf-8

import logging
from logging.handlers import TimedRotatingFileHandler

from base.config.settings import log_filename
from base.config.settings import log_logger


def retrieve_log(log_file_name, _logger):
    log_filename = log_file_name
    log_handler = TimedRotatingFileHandler(log_filename, when="midnight")
    log_formatter = logging.Formatter(
        '%(asctime)-6s %(name)s %(module)s %(funcName)s %(lineno)d - %(levelname)s %(message)s')
    log_handler.setFormatter(log_formatter)

    log = logging.getLogger(_logger)
    log.propagate = False
    log.addHandler(log_handler)
    log.setLevel(logging.DEBUG)

    return log


log = retrieve_log(log_filename, log_logger)
