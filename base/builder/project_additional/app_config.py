# coding= utf-8

__APP_NAME__
__APP_DESCRIPTION__
__PORT__
__APP_PREFIX__
__APP_VERSION__
models = [
    'src.models.utils',
    'src.models.sequencers',
    'src.models.user',
]
imports = [
    'src.api.utils.options',
    'src.api.utils.hash2params',
    'src.api.user.login',
]
db_type = 'mysql'
db_config = {
    'db_name': __APP_DB_NAME__,
    'db_user': '__db_username__',
    'db_password': '__db_user_password__',
    'db_host': '__db_host__',
    'db_port': '__db_port__',
}
response_messages_module = 'src.lookup.response_messages'
debug = True
