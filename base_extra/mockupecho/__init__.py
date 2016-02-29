APP_NAME = 'mockupecho'
PREFIX = 'api'
IMPORTS = [
    'echo'
]
SHOW_SPECS = True
DB_CONF = '{}.config.echoconfig'.format(APP_NAME)
SVC_PORT = 8600
TESTS = 'tests'
BASE_TEST = True
# MSG_LOOKUP = 'messages_file'
# APP_VERSION = '0.0.1'
# APP_HOOKS = 'apphooks'
# LB = False    # True for load balancer application
# BALANCE = ['127.0.0.1:{}'.format(7700+x) for x in range(40)] # balance server address list
