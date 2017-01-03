# coding= utf-8

import argparse
import tornado.web
import tornado.ioloop

from base.application.components import BaseHandler
from base.application.components import DefaultRouteHandler
from base.application.helpers.exceptions import MissingApplicationPort
from base.application.helpers.importer import load_application
from base.application.helpers.importer import load_orm

import base.config.application_config


def check_arguments():

    argparser = argparse.ArgumentParser(description=base.config.application_config.app_description)
    argparser.add_argument('-p', '--port', help='the port on which application will listen')
    return argparser.parse_args()


def _get_svc_port():

    from base.config.application_config import port as svc_port
    return svc_port


class Application(tornado.web.Application):

    def __init__(self, entries):

        self.entries = entries

        super(Application, self).__init__(
            self.entries,
            debug=base.config.application_config.debug,
            cookie_secret=base.config.application_config.secret_cookie,
            default_handler_class=DefaultRouteHandler
        )


def engage():

    args = check_arguments()

    entries = [(BaseHandler.__URI__, BaseHandler), ]
    load_application(entries, args.port)

    svc_port = _get_svc_port()
    if not svc_port:
        raise MissingApplicationPort('Application port not configured or missing from command line options')

    load_orm(svc_port)

    app = Application(entries)

    start_message = 'starting {} {} service on {}: http://localhost:{}'.format(
        base.config.application_config.app_name,
        base.config.application_config.app_version,
        svc_port, svc_port)

    from base.common.utils import log
    print(start_message)
    log.info(start_message)
    app.listen(svc_port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':

    engage()

