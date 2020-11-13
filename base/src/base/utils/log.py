import logfmt
import logging
import re
import traceback

import aiotask_context as context

LOG_CONTEXT = 'log_context'


def get_log_context():

    log_context = context.get(LOG_CONTEXT)
    if log_context is None:
        log_context = {}
        context.set(LOG_CONTEXT, log_context)
    return log_context


def set_log_context(**kwargs):
    log_context = get_log_context()
    log_context.update(kwargs)


def clear_log_context():
    log_context = get_log_context()
    log_context.clear()


def log(logger: logging.Logger, lvl: int, include_context: bool = False, **kwargs):

    all_info = {**get_log_context(), **kwargs} if include_context else kwargs

    info = {
        k: v for k, v in all_info.items()
        if k not in ['exc_info', 'stack_info', 'extra']
    }

    exc_info = all_info.get('exc_info')
    if exc_info:  # tuple (typ, value, tb)
        trace = '\t'.join(traceback.format_exception(*exc_info))
        current_frame = exc_info[2]
        while current_frame.tb_next is not None:
            current_frame = current_frame.tb_next

        info['file'] = current_frame.tb_frame.f_code.co_filename
        info['line'] = current_frame.tb_lineno
        # info['trace'] = re.sub(r'[\r\n]+', '\t', trace)

    msg = next(logfmt.format(info))

    logger.log(lvl, msg,)
