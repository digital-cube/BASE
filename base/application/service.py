# coding= utf-8

import argparse
import tornado.web
import tornado.ioloop

import base.application.components
from base.application.components import BaseHandler
from base.application.components import DefaultRouteHandler
from base.application.helpers.exceptions import MissingApplicationPort
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


def engage():

    args = check_arguments()

    entries = [(BaseHandler.__URI__, BaseHandler), ]
    load_application(entries, args.port)

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


if __name__ == '__main__':

    engage()

