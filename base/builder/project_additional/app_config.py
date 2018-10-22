# coding= utf-8

__APP_NAME__
__APP_DESCRIPTION__
__PORT__
__APP_PREFIX__
__APP_VERSION__

read_only_ports=[]
ro_ports_length = len(read_only_ports)
simulate_balancing = True

imports = [
    'src.api.hello',
]
db_type = 'mysql'
# db_config = 'db_config.json'
# api_hooks = 'src.api_hooks.hooks'
# session_storage = 'DB'  # 'DB'|'REDIS'
response_messages_module = 'src.lookup.response_messages'
# user_roles_module = 'src.lookup.user_roles'
support_mail_address = 'support@test.loc'
support_name = 'support@test'
# strong_password = False
debug = True
# forgot_password_lending_address = 'http://localhost:8802/user/password/change'
# forgot_password_message_subject = 'Forgot password request'
# forgot_password_message = '''
# We have received request for reset Your password.
# Please follow the link bellow to set Your new password:
# {}
#
# If You didn't request password change, please ignore this message.
#
# Best Regards
# '''
static_path = None
static_uri = None
log_directory = './log'
register_allowed_roles = None
registrators_allowed_roles = None
pre_app_processes = None    # [(app_name, app_cmd_for_subprocess, redirect_output)]
post_app_processes = None   # [(app_name, app_cmd_for_subprocess, redirect_output)]
google_client_ID = None
count_calls = False    # count every call to uri and method
