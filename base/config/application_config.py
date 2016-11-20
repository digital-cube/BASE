# coding= utf-8

from base.config.settings import app

port = None
app_name = app['name'][0]
app_prefix = app['prefix'][0]
app_version = app['version'][0]
app_description = app['description'][0]
secret_cookie = 'cookie_secrete'
debug = True
orm_models = {}
