# coding= utf-8

app_builder_description = '''
    Base application builder
'''

app_subcommands_title = '''basemanager commands'''
app_subcommands_description = '''
    get help for available commands with: command -h
'''

# key: default argument value, value: argument help
app = {
    'cmd': (None, 'basemanager command to execute'),
    'description': ('base application', 'the new application description'),
    'destination': ('.', 'the destination directory'),
    'name': (None, 'the new application name'),
    'version': ('0.0.1', 'the new application version'),
    'prefix': ('api', 'the new application api calls prefix'),
    'port': (8802, 'the port for the new application'),
    'database_type': ('mysql', 'type od the sql database'),
    'database_name': (None, 'the name for database'),
    'database_username': (None, 'database user name'),
    'database_password': (None, 'database user password'),
    'database_host': ('localhost', 'database host name'),
    'database_port': ({'mysql': 3306, 'postgresql': 5432, 'sqlite': 5555}, 'database port'),
    'table_name': (None, 'name of the table to create'),
}
template_project_folder = 'template_project'
project_additional_folder = 'project_additional'
db_init_warning = '''
#################################################
#                                               #
#               W A R N I N G                   #
#                                               #
#   Can not find configuration to initialize    #
#   database. Please check that you are in      #
#   project directory and try again.            #
#                                               #
#################################################
'''


log_directory = '/var/log/base'
log_filename = '{}/base_v1.log'.format(log_directory)
log_logger = 'BASEv1'
log = None
