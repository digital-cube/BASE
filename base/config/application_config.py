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
db_configured = False
db_type = None
strong_password = False
api_hooks = None
models = []
orm_models = {}
imports = [
    'base.application.api.user.change_password',
    'base.application.api.user.login',
    'base.application.api.user.logout',
    'base.application.api.user.forgot',
    'base.application.api.user.register',
    'base.application.api.utils.options',
    'base.application.api.utils.hash2params',
    'base.application.api.utils.mail_queue',
]
session_storage = 'DB'
user_roles_module = 'src.lookup.user_roles'
support_mail_address = 'support@test.loc'
support_name = 'support@test'
forgot_password_lending_address = 'http://localhost:8802/user/password/change'
forgot_password_message_subject = 'Forgot password request'
forgot_password_message = '''
We have received request for reset Your password.
Please follow the link bellow to set Your new password:
{}

If You didn't request password change, please ignore this message.

Best Regards
'''
static_path = None
static_uri = ''
log_directory = './log'
register_allowed_roles = None
registrators_allowed_roles = None
