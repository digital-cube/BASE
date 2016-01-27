from base_lookup.api_messages import msgs


def error(s, **kwargs):

    http_status = 400   # bad request

    if 'http_status' in kwargs:
        http_status = kwargs['http_status']
        del kwargs['http_status']

    if isinstance(s, str):
        return {'message': s, 'code': 0, 'http_status': http_status }

    if s not in msgs:
        return {'message': 'unknown error', 'code': 0, 's': s, 'http_status': http_status }

    return {'message': msgs[s], 'code': s, 'params': kwargs, 'http_status': http_status}


def res_ok(s=None, **kwargs):

    http_status = 204

    if s or kwargs != {}:
        http_status = 200

    if 'http_status' in kwargs:
        http_status = kwargs['http_status']
        del kwargs['http_status']

    response = {}
    response.update(kwargs)
    if isinstance(s, str):
        response['message'] = s

    if isinstance(s, dict):
        response.update(s)

    if isinstance(s, int):
        if s in msgs:
            response.update({'message': msgs[s], 'code': s})

    if response:
        return {'http_status': http_status, 'params': response}

    return {'http_status':http_status}


def put_ok(s=None, **kwargs):
    return res_ok(s, **kwargs)


def delete_ok(s=None, **kwargs):
    return res_ok(s, **kwargs)


def get_ok(s=None, **kwargs):
    return res_ok(s, **kwargs)


def post_ok(s=None, **kwargs):
    return res_ok(s, **kwargs)



