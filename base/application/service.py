# coding= utf-8

import os
import argparse
import tornado.web
import tornado.ioloop

import base.application.components
from base.application.components import BaseHandler
from base.application.components import DefaultRouteHandler
from base.application.helpers.exceptions import MissingApplicationPort
from base.application.helpers.exceptions import PreApplicationProcessConfigurationError
from base.application.helpers.exceptions import PostApplicationProcessConfigurationError
from base.application.helpers.importer import load_application
from base.application.helpers.importer import load_orm

import base.config.application_config


def check_arguments():

    argparser = argparse.ArgumentParser(description=base.config.application_config.app_description)
    argparser.add_argument('-p', '--port', help='the port on which application will listen')
    argparser.add_argument('-x', '--prefix', help='prefix for all application routes')
    return argparser.parse_args()


def _get_svc_port():

    from base.config.application_config import port as svc_port
    return svc_port


class Application(tornado.web.Application):

    def __init__(self, entries):

        self.entries = entries

        _settings = {}
        if base.config.application_config.static_path and base.config.application_config.static_uri:
            self.entries.append((base.config.application_config.static_uri, tornado.web.StaticFileHandler))
            _settings['static_path'] = base.config.application_config.static_path

        super(Application, self).__init__(
            self.entries,
            debug=base.config.application_config.debug,
            cookie_secret=base.config.application_config.secret_cookie,
            default_handler_class=DefaultRouteHandler,
            **_settings
        )


def _make_extra_prefix(prefix, svc_port):
    return '{}{}'.format(prefix, svc_port)


def _add_prefix(entries, prefix, svc_port):
    _new_entries = []
    _extra_prefix = _make_extra_prefix(prefix, svc_port)
    for e in entries:
        _new_entries.append(('/{}{}'.format(_extra_prefix, e[0]), e[1]))

    return _new_entries


def _engage(args, entries):

    svc_port = _get_svc_port()
    if not svc_port:
        raise MissingApplicationPort('Application port not configured or missing from command line options')

    if args.prefix is not None:
        setattr(base.application.components.Base, 'extra_prefix', _make_extra_prefix(args.prefix, svc_port))
        entries = _add_prefix(entries, args.prefix, svc_port)

    load_orm(svc_port)

    app = Application(entries)
    setattr(app, 'svc_port', svc_port)

    start_message = 'starting {} {} service on {}: http://localhost:{}{}'.format(
        base.config.application_config.app_name,
        base.config.application_config.app_version,
        svc_port, svc_port,
        ' with api prefix /{}{}'.format(args.prefix, svc_port) if args.prefix is not None else '')

    from base.common.utils import log
    print(start_message)
    log.info(start_message)
    app.listen(svc_port)
    tornado.ioloop.IOLoop.instance().start()


def _start_app_processes(app):

    from base.common.utils import log
    import subprocess

    def _log(msg):
        print(msg)
        log.info(msg)
    _log('Starting {}'.format(app[0]))
    try:
        if app[2]:  # if redirect output
            p = subprocess.Popen(app[1], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        else:
            p = subprocess.Popen(app[1])
    except FileNotFoundError:
        _msg = 'Can not find process {}'.format(app[0])
        log.error(_msg)
        raise
    _log('{} started: PID {}'.format(app[0], p.pid))


def _start_pre_app_processes():

    # [(app_name, app_cmd_for_subprocess, redirect_output)]
    for app in base.config.application_config.pre_app_processes:
        _start_app_processes(app)

    return True


def _start_post_app_processes():

    # [(app_name, app_cmd_for_subprocess, redirect_output)]
    for app in base.config.application_config.post_app_processes:
        _start_app_processes(app)

    return True


def _engage_with_process(args, entries):

    from base.common.utils import log
    if base.config.application_config.pre_app_processes is not None:

        if type(base.config.application_config.pre_app_processes) != list:
            log.error('Invalid type in configuration for pre application processes')
            raise PreApplicationProcessConfigurationError('Pre application processes has to be a list')
        if any([type(x) != tuple for x in base.config.application_config.pre_app_processes]) or \
                any([len(x) != 3 for x in base.config.application_config.pre_app_processes]):
            log.error('Invalid configuration for pre application processes. Processes has to be declared as a tuple of a name and a command')
            raise PreApplicationProcessConfigurationError('Pre application processes has to be tuples in a list')

        if not _start_pre_app_processes():
            log.error('Could not start pre application processes')

    if base.config.application_config.post_app_processes is not None:

        if type(base.config.application_config.post_app_processes) != list:
            log.error('Invalid type in configuration for post application processes')
            raise PostApplicationProcessConfigurationError('Post application processes has to be a list')
        if any([type(x) != tuple for x in base.config.application_config.post_app_processes]) or \
                any([len(x) != 3 for x in base.config.application_config.post_app_processes]):
            log.error('Invalid configuration for post application processes. Processes has to be declared as a tuple of a name and a command')
            raise PostApplicationProcessConfigurationError('Post application processes has to be tuples in a list')

        tornado.ioloop.IOLoop.current().add_callback(_start_post_app_processes)

    _engage(args, entries)


def engage(starter_path):

    args = check_arguments()

    entries = [(BaseHandler.__URI__, BaseHandler), ]
    load_application(entries, args.port)
    entries.append((r"/static/(.*)", tornado.web.StaticFileHandler,
                    {"path": "{}/static".format(os.path.dirname(starter_path))}))

    _engage_with_process(args, entries)

