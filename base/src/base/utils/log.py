import os
import re
import logfmt
import logging
import traceback
import aiotask_context as context

import base

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
        print(traceback.print_exc())
        trace = '\t'.join(traceback.format_exception(*exc_info))

        if not base.registry.test:
            print(traceback.print_exc())

        current_frame = exc_info[2]
        while current_frame.tb_next is not None:
            current_frame = current_frame.tb_next

        info['file'] = current_frame.tb_frame.f_code.co_filename
        info['line'] = current_frame.tb_lineno
        info['trace'] = re.sub(r'[\r\n]+', '\t', trace)

    msg = next(logfmt.format(info))

    logger.log(lvl, msg,)

def message_from_context():
    context = get_log_context()
    _error_info = context['exc_info']
    _error_class = _error_info[0].__name__
    _error_value = _error_info[1]
    _exc_tb = _error_info[2]
    _file = os.path.split(_exc_tb.tb_frame.f_code.co_filename)[1]
    _list = '{}({})'.format(_file, _exc_tb.tb_lineno)
    _n = _exc_tb.tb_next
    _c = None
    while _n:
        _fname = os.path.split(_n.tb_frame.f_code.co_filename)[1]
        _list += ' -> {}({})'.format(_fname, _n.tb_lineno)
        _c = '{}({})'.format(_n.tb_frame.f_code.co_name, _n.tb_lineno)
        _n = _n.tb_next

    _value = f'({_error_value.id_message}) {_error_value.message}'  if hasattr(_error_info, 'id_message') else _error_value
    return f"{_list} {'-> {} '.format(_c) if _c else ''}-> {_error_class}: {_value}"