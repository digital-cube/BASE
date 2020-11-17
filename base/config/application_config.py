# coding= utf-8

from base.config.settings import app

master = True
port = None
read_only_ports = []
ro_ports_length = len(read_only_ports)
simulate_balancing = True


app_name = app['name'][0]
app_prefix = app['prefix'][0]
app_version = app['version'][0]
app_description = app['description'][0]
secret_cookie = 'cookie_secret'
secret_cookie_name = 'token'
debug = True
db_config = None
db_configured = False
db_type = None
strong_password = False
reload_session = False  # for balancers to be able to get changes from slave database
api_hooks = None
models = []
orm_models = {}
imports = [
    'base.application.api.user.change_password',
    'base.application.api.user.login',
    'base.application.api.user.logout',
    'base.application.api.user.forgot',
    'base.application.api.user.register',
    'base.application.api.user.faccess',
    'base.application.api.user.gaccess',
    'base.application.api.utils.options',
    'base.application.api.utils.hash2params',
    'base.application.api.utils.mail_queue',
]
session_storage = 'DB'
user_roles_module = 'src.lookup.user_roles'
languages_module = 'src.lookup.languages'
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
pre_app_processes = None    # [(app_name, app_cmd_for_subprocess, redirect_output)]
post_app_processes = None   # [(app_name, app_cmd_for_subprocess, redirect_output)]
service_initialisation_callbacks = None     # [(module, function_from_module)] -> eg: [('src.init', 'start')]
google_client_ID = None
google_discovery_docs_url = 'https://accounts.google.com/.well-known/openid-configuration'
google_check_access_token_url = 'https://www.googleapis.com/oauth2/v3/tokeninfo'
seconds_before_shutdown = 0     # seconds before SIGTERM will occur
count_calls = False    # count every call to uri and method
count_call_log = 'log/count_call.log'
count_call_file = 'log/count_call.json'

entry_points_extended = {}
balanced_readonly_get = set()
authentication_type = 'TOKEN'
cookie_domain = None                # domain name for cookies
test_mode = False
session_expiration_timeout = None   # seconds for session's token timeout
disable_spec = False                # disable spec URI
disable_all_paths = False           # disable all paths URI
cached_session = True               # use cached session from orm, or always create a new session