# coding= utf-8

app_builder_description = '''
    Base application builder
'''
app = {
    'cmd': (None, 'basemanager command to execute'),
    'description': ('base application', 'the new application description'),
    'destination': ('.', 'the destination directory'),
    'name': (None, 'the new application name'),
    'version': ('0.00.1', 'the new application version'),
    'prefix': ('api', 'the new application api calls prefix'),
    'port': (8802, 'the port for the new application')
}
available_builder_commands = ['init']
template_project_folder = 'template_project'
project_additional_folder = 'project_additional'


log_directory = '/var/log/base'
log_filename = '{}/base_v1.log'.format(log_directory)
log_logger = 'BASEv1'
log = None
