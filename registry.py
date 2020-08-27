import redis
import json

_services = {}
_last = None

test = False
test_port = None


def register(svc_name, service):
    global _services, _last
    _services[svc_name] = service
    _last = svc_name

    r = redis.Redis()
    r.set('base_svc_'+svc_name, json.dumps(service))

def address(svc_name):
    if not test:
        return f"http://localhost:{port(svc_name)}"

    return f"http://localhost:{test_port}"


def port(svc_name=None):

    if test:
        return test_port

    global _services, _last

    if not svc_name:
        svc_name = _last
    else:
        if svc_name not in _services:
            r = redis.Redis()
            _s = r.get('base_svc_'+svc_name)
            if _s:
                _services[svc_name] = json.loads(_s.decode('utf-8'))

    if svc_name in _services and 'port' in _services[svc_name]:
        return _services[svc_name]['port']
    return None


def prefix(svc_name=None):
    global _services, _last

    if not svc_name:
        svc_name = _last

    else:
        if svc_name not in _services:
            r = redis.Redis()
            _s = r.get('base_svc_'+svc_name)
            if _s:
                _services[svc_name] = json.loads(_s.decode('utf-8'))

    if svc_name in _services and 'prefix' in _services[svc_name]:
        return _services[svc_name]['prefix']
    return None
