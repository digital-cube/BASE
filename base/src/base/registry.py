from .store import Store
import json
from os.path import expanduser

_services = {}
_last = None

test = False
test_port = None


def registered(svc_name):
    global test
    if test:
        return svc_name in _services

    # for monolit apps
    if svc_name in _services:
        return svc_name

    # for distributed apps
    return Store.exists('base_svc_' + svc_name)

def register(service: dict):
    if 'storage' in service and "~" in service['storage']:
        service['storage'] = service['storage'].replace('~', expanduser("~"))
        service['storage'] = service['storage'].strip()
        if service['storage'][-1] != '/':
            service['storage'] = service['storage'] + '/'

    if 'static' in service:
        if service['static'][-1] != '/':
            service['static'] = service['static'] + '/'

    global _services, _last
    _services[service['name']] = service
    _last = service['name']

    from .config import config
    if 'store' in config.conf:
        Store.set_engine(config.conf['store'])

    Store.set('base_svc_' + service['name'], json.dumps(service))

    if not Store.exists('services'):
        s_services = list(_services.keys())
        Store.set('services', json.dumps(s_services))
    else:
        s_services = json.loads(Store.get('services'))
        s_services = set(s_services)
        s_services.add(service['name'])
        s_services = list(s_services)
        Store.set('services', json.dumps(s_services))


def address(svc_name):
    if not test:

        r_svc = json.loads(Store.get('base_svc_' + svc_name))

        if 'service' in r_svc:
            return r_svc['service']

        return f"http://localhost:{port(svc_name)}"

    return f"http://localhost:{test_port}"


def service(svc_name=None):
    global _services, _last

    if not svc_name:
        svc_name = _last
    else:
        if svc_name not in _services:
            _s = Store.get('base_svc_' + svc_name)
            if _s:
                _services[svc_name] = json.loads(_s.decode('utf-8'))

    if svc_name in _services:
        return _services[svc_name]

    return None


def port(svc_name=None):
    if test:
        return test_port

    s = service(svc_name)
    return s['port'] if s and 'port' in s else None


def info(svc_name=None):
    if test:
        return "INFO"

    s = service(svc_name)
    inf = f'port: {port(svc_name)};'

    d = db(svc_name)
    if d:
        inf += f'db: {d["host"]}/{d["database"]}'

    return inf


def prefix(svc_name=None):
    s = service(svc_name)
    return s['prefix'] if s and 'prefix' in s else ''  # f'/api/{svc_name}'


def db(svc_name=None):
    s = service(svc_name)
    return s['db'] if s and 'db' in s else None


def public_key() -> str:
    pubkey = Store.get('users_service_public_key').decode('utf-8')#['keys']['public']
    return pubkey


def private_key() -> str:
    from base import config
    return config.conf['private_key']
