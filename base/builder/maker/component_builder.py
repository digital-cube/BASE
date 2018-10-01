import os
import sys
import json
import importlib

from base.application.lookup import exit_status
from base.config.settings import available_BASE_components
from base.builder.maker.components.blog_builder import add_blog
from base.builder.maker.components.site_builder import add_site


def add_component(parsed_args):

    if parsed_args.component not in available_BASE_components:
        print('''
        Component "{}" not recognized,
        please use 'db_init list' to see available components
        '''.format(parsed_args.component))
        sys.exit(exit_status.BASE_COMPONENT_NOT_EXISTS)

    if parsed_args.component == 'blog':
        add_blog()

    if parsed_args.component == 'site':
        add_site()


def list_components(parsed_args):
    msg = '''
    available components: {}
    '''.format(''.join(['\n\t{}'.format(c) for c in available_BASE_components]))
    print(msg)

