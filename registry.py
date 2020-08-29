import redis
import json
from os.path import expanduser

_services = {}
_last = None

test = False
test_port = None


def register(svc_name, service):
    if 'storage' in service and "~" in service['storage']:
        service['storage'] = service['storage'].replace('~', expanduser("~"))

    global _services, _last
    _services[svc_name] = service
    _last = svc_name

    r = redis.Redis()
    r.set('base_svc_' + svc_name, json.dumps(service))


def address(svc_name):
    if not test:
        return f"http://localhost:{port(svc_name)}"

    return f"http://localhost:{test_port}"


def service(svc_name=None):
    global _services, _last

    if not svc_name:
        svc_name = _last
    else:
        if svc_name not in _services:
            r = redis.Redis()
            _s = r.get('base_svc_' + svc_name)
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


def prefix(svc_name=None):
    s = service(svc_name)
    return s['prefix'] if s and 'prefix' in s else None


def db(svc_name=None):
    s = service(svc_name)
    return s['db'] if s and 'db' in s else None


def private_key():
    return '''-----BEGIN PRIVATE KEY-----
MIIBVQIBADANBgkqhkiG9w0BAQEFAASCAT8wggE7AgEAAkEA1ydZ+1PJEM2uLYnL
keYJ7TK3wjfBX3kKgS2gL6S/KnMCwj8fE1RL74O2A20LtDSXUa0hFXNTJn2ve+7w
Aor9CwIDAQABAkEAlloTkYR9j9aMD5qpva1J5o54x6p64aMOajNeK60vQhOP+hW8
dU9kOT8AYXKE73OkftCNgQ5HEXsuy6DskWOJgQIhAP96FkLJwpZ5slVCvVXotq7P
QH92RKKx04M6arau6KOhAiEA15gg3TWdU7Pvh/2FNBQ4/JuSihGYSlfgROFAS8hH
4SsCIFjJHSNo6u9Qq+FlqFdK4PIvpMKnX4MLOe7JRnzmnIMBAiAxHwQ94n1aGOE2
htjWqNTjGT8mHiQorCT5DKltmtBlyQIhAMPgHzKaop3nNrUtjLe2U0vDPh/Jpm4Q
NtgFwgPuCyhu
-----END PRIVATE KEY-----'''


def public_key():
    return '''-----BEGIN RSA PUBLIC KEY-----
MEgCQQDXJ1n7U8kQza4ticuR5gntMrfCN8FfeQqBLaAvpL8qcwLCPx8TVEvvg7YD
bQu0NJdRrSEVc1Mmfa977vACiv0LAgMBAAE=
-----END RSA PUBLIC KEY-----'''
