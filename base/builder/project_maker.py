# coding= utf-8

import os
import sys
import json
import shutil
import argparse
import platform

import base

from base.config.settings import app
from base.config.settings import app_builder_description
from base.config.settings import app_subcommands_title
from base.config.settings import app_subcommands_description

from base.builder.maker.project_builder import build_project
from base.builder.maker.database_builder import build_database
from base.builder.maker.database_builder import build_database_with_alembic
from base.builder.maker.database_helpers import show_create_table
from base.builder.maker.playground_builder import create_playground
from base.builder.maker.component_builder import list_components
from base.builder.maker.component_builder import add_component

import base.common.orm


__project_path = None
__WINDOWS__ = platform.system() == 'Windows'


def pars_command_line_arguments():

    argparser = argparse.ArgumentParser(description=app_builder_description)

    subparsers = argparser.add_subparsers(title=app_subcommands_title, description=app_subcommands_description,
                                          help='choose from available commands', dest='cmd')
    subparsers.required = True

    init_parser = subparsers.add_parser('init', help='initialize base project', aliases=['i'])
    init_parser.add_argument('name', type=str, help=app['name'][1])
    init_parser.add_argument('-D', '--destination', default=app['destination'][0], help=app['destination'][1])
    init_parser.add_argument('-d', '--description', default=app['description'][0], help=app['description'][1])
    init_parser.add_argument('-p', '--port', default=app['port'][0], help=app['port'][1])
    init_parser.add_argument('-v', '--version', default=app['version'][0], help=app['version'][1])
    init_parser.add_argument('-x', '--prefix', default=app['prefix'][0], help=app['prefix'][1])

    _splitter = '\\' if __WINDOWS__ else '/'
    db_init_parser = subparsers.add_parser('db_init', help="create base project's database schema", aliases=['dbi'])
    db_init_parser.add_argument('-dt', '--database_type', default=app['database_type'][0], help=app['database_type'][1])
    db_init_parser.add_argument('-dn', '--database_name', default=os.getcwd().split(_splitter)[-1],
                                help=app['database_name'][1])
    db_init_parser.add_argument('-dh', '--database_host', default=app['database_host'][0], help=app['database_host'][1])
    db_init_parser.add_argument('-dp', '--database_port', help=app['database_port'][1])
    db_init_parser.add_argument('-p', '--application_port', help=app['port'][1], type=str)
    db_init_parser.add_argument('-a', '--add_action_logs', default=app['add_action_logs'][0],
                                help=app['add_action_logs'][1], type=bool)
    db_init_parser.add_argument('user_name', type=str, help=app['database_username'][1])
    db_init_parser.add_argument('password', type=str, help=app['database_password'][1])

    db_init_alembic_parser = subparsers.add_parser('db_init_alembic', help="create base project's database schema when alembic structure is present",
                                                   aliases=['dba'])

    show_create_parser = subparsers.add_parser('db_show_create', help="show sql create table query", aliases=['dbs'])
    show_create_parser.add_argument('table_name', type=str, help=app['table_name'][1])

    playground_parser = subparsers.add_parser('playground',
                                              help="create api playground frontend with nginx virtual host",
                                              aliases=['p'])

    add_plugin_parser = subparsers.add_parser('add', help="add a component to the BASE project", aliases=['a'])
    add_plugin_parser.add_argument('component', type=str, help=app['component'][1])

    list_plugins_parser = subparsers.add_parser('list', help="list available BASE components", aliases=['l'])

    argparser.add_argument('-V', '--version', action='version', help='show BASE version',
                           version='BASE v{}'.format(base.__VERSION__))

    return argparser.parse_args()


def execute_builder_cmd():

    parsed_args = pars_command_line_arguments()

    if parsed_args.cmd in ['init', 'i']:
        build_project(parsed_args)

    if parsed_args.cmd in ['db_init', 'dbi']:
        build_database(parsed_args)

    if parsed_args.cmd in ['db_init_alembic', 'dba']:
        build_database_with_alembic(parsed_args)

    if parsed_args.cmd in ['db_show_create', 'dbs']:
        show_create_table(parsed_args)

    if parsed_args.cmd in ['playground', 'p']:
        create_playground(parsed_args)

    if parsed_args.cmd in ['add', 'a']:
        add_component(parsed_args)

    if parsed_args.cmd in ['list', 'l']:
        list_components(parsed_args)

