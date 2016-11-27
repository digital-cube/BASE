# coding= utf-8

from base.config.settings import app

port = None
app_name = app['name'][0]
app_prefix = app['prefix'][0]
app_version = app['version'][0]
app_description = app['description'][0]
secret_cookie = 'cookie_secrete'
debug = True
db_config = None
db_type = None
strong_password = False
api_hooks = None
models = []
orm_models = {}
imports = [
    'base.application.api.user.login',
    'base.application.api.user.logout',
    'base.application.api.user.register',
]
session_storage = 'DB'
user_roles_module = 'src.lookup.user_roles'

