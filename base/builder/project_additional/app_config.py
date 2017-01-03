# coding= utf-8

__APP_NAME__
__APP_DESCRIPTION__
__PORT__
__APP_PREFIX__
__APP_VERSION__
models = [
    'src.models.mail',
    'src.models.sequencers',
    'src.models.session',
    'src.models.user',
    'src.models.utils',
]
imports = [
    'src.api.hello',
]
db_type = 'mysql'
db_config = {
    __DB_PORT_CONFIG__: {
        'db_name': __APP_DB_NAME__,
        'db_user': '__db_username__',
        'db_password': '__db_user_password__',
        'db_host': '__db_host__',
        'db_port': '__db_port__',
    }
}
api_hooks = 'src.api_hooks.hooks'
session_storage = 'DB'  # 'DB'|'REDIS'
response_messages_module = 'src.lookup.response_messages'
user_roles_module = 'src.lookup.user_roles'
support_mail_address = 'support@test.loc'
support_name = 'support@test'
strong_password = False
debug = True
forgot_password_lending_address = 'http://localhost:8802/user/password/change'
forgot_password_message_subject = 'Forgot password request'
forgot_password_message = '''
We have received request for reset Your password.
Please follow the link bellow to set Your new password:
{}

If You didn't request password change, please ignore this message.

Best Regards
'''
