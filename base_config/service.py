import logging
from logging.handlers import TimedRotatingFileHandler
from base_config.settings import APPS, LOG_DIR


port = 8800
svc_prefix = 'echo'
svc_url = 'http://localhost:{}/{}'.format(port, svc_prefix)

support_mail = 'support@digital.com'

logs = {}

for app in APPS:
    app_log_name = app.split('/')[-1]
    _log_filename = "{}/{}.log".format(LOG_DIR, app_log_name.lower())
    _log_handler = TimedRotatingFileHandler(_log_filename, when="midnight")
    _log_formatter = logging.Formatter(
            '%(asctime)-6s %(name)s %(module)s %(funcName)s %(lineno)d - %(levelname)s %(message)s')
    _log_handler.setFormatter(_log_formatter)

    _log = logging.getLogger('DGT{}'.format(app_log_name.upper()))
    _log.propagate = False
    _log.addHandler(_log_handler)
    _log.setLevel(logging.DEBUG)

    logs[app_log_name] = _log

log_filename = "{}/digital.log".format(LOG_DIR)
log_handler = TimedRotatingFileHandler(log_filename, when="midnight")
log_formatter = logging.Formatter(
        '%(asctime)-6s %(name)s %(module)s %(funcName)s %(lineno)d - %(levelname)s %(message)s')
log_handler.setFormatter(log_formatter)

log = logging.getLogger('DGTL')
log.propagate = False
log.addHandler(log_handler)
log.setLevel(logging.DEBUG)

