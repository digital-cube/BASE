import re
import json
import base_config.settings as csettings
from base_common.importer import get_pkgs
from base_config.settings import  __VERSION__


def fdoc_parser_old(doc):

    try:
        docl = doc.split('\n')
    except AttributeError:
        return 'Missing docstring'

    desc = ''
    params = {}
    _return = {}
    auth = {}

    ps = ':(?P<grp>\w+)\s*(?P<prm>\w+)\s*:\s*(?P<desc>[^,]+)\s*,\s*(?P<tp>[^,]+)\s*,\s*(?P<req>\w+)$'
    rs = ':(?P<grp>\w+)\s*:\s*(?P<tp>\d+)\s*,?\s*(?P<desc>.*)?$'
    sa = ':(?P<grp>\w+)\s*:\s*(?P<desc>.*)?$'

    for l in docl:

        l = l.strip()
        p = re.match(r':(?P<grp>\w+)', l)
        if p:
            grp = p.group('grp')

            if grp == 'param':
            
                m = re.match(ps,l)

                param = m.group('prm')

                if param not in params:
                    params[param] = {}

                params[param]['description'] = m.group('desc')
                params[param]['type'] = m.group('tp')
                params[param]['req'] = m.group('req')

            elif grp == 'return':
                m = re.match(rs, l)
                ret = m.group('tp')
                if ret not in _return:
                    _return[ret] = {}
                mdesc = m.group('desc')
                _return[ret]['description'] = mdesc if mdesc else 'No content'

            elif grp == 'Authorization':
                a = re.match(sa, l)
                a_desc = a.group('desc')
                auth['description'] = a_desc

        else:
            if l:
                desc = l

    return {'description':desc, 'authorization': auth, 'parameters': params, 'return': _return}


def parse_module_desc(docstr):

    dd = '(?P<desc>[^:]+)\s*:description:\s*(?P<long_desc>[\w,\s]*)'
    dd1 = '(?P<desc>[^:]+)\s*'
    try:
        pp = re.match(dd, docstr)
        if not pp:

            pp = re.match(dd1, docstr)
            if not pp:
                return 'Missing description', False

            short_d = pp.group('desc')

            return short_d, False

        short_d = pp.group('desc')
        long_d = pp.group('long_desc')

    except:
        short_d = 'Missing description'
        long_d = 'Missing description'

    return short_d, long_d


def _get_fdoc_parsed(func):

    if not func.__doc__:
        return None, None

    dd = '(?P<desc>[^:]+)\s*:description:\s*(?P<long_desc>[\w,\s]*)'
    try:
        pp = re.match(dd, func.__doc__)
        if not pp:

            return None, None

        short_d = pp.group('desc')
        long_d = pp.group('long_desc')
        return short_d, long_d
    except:
        return None, None


def fdoc_parser(url_methods, func):

    _m = func.__api_method_type__
    if _m not in url_methods:
        url_methods[_m] = {}

    url_methods[_m]['name'] = func.__name__
    url_methods[_m]['func_description'], url_methods[_m]['func_description_long'] = _get_fdoc_parsed(func)
    # url_methods[_m]['description'] = func.__doc__.strip() if func.__doc__ else None
    url_methods[_m]['parameters'] = {}
    url_methods[_m]['return'] = {"204": {"description": "No content"}}
    try:
        url_methods[_m]['authorization'] = func.__api_authenticated__
    except:
        # print(func.__name__, 'nema auth')
        url_methods[_m]['authorization'] = False

    # try:
    if hasattr(func, '__app_api_arguments__'):
        for p in func.__app_api_arguments__:

            url_methods[_m]['parameters'][p[0]] = {
                'description': p[1],
                'type': p[2],
                'req': p[3]
            }

            if p[4]:
                url_methods[_m]['parameters'][p[0]]['example'] = p[4]

    # except AttributeError as e:
    #     print('READ DOCUMENT EXCEPTION: {}'.format(e))

    if func.__api_return__:
        for r in func.__api_return__:
            url_methods[_m]['return'][r[0]] = {
                'description': r[1]
            }


def doc_parser(doc, url_prefix, base_pkg):

    short_desc, long_desc = parse_module_desc(doc.__doc__)
    api = {
        'doc_description': short_desc.strip() if short_desc else short_desc,
        'doc_description_long': long_desc.strip() if long_desc else long_desc,
        'urls': {}}

    for f in doc.__api_methods__:

        if hasattr(f,'__api_method_call__') and f.__api_method_call__:

            _url = '/{}'.format(doc.location) if base_pkg else '/{}/{}'.format(url_prefix, doc.location)
            if f.__api_path__:
                _url += '/{}'.format(f.__api_path__)

            if _url not in api['urls']:
                api['urls'][_url] = {}

            fdoc_parser(api['urls'][_url], f)

    return api


def get_api_specification(request, *args, **kwargs):

    applist = {'api_version': __VERSION__}

    applications = {}

    if len(csettings.APPS):

        installed_apps = {}
        get_pkgs(installed_apps)

        for app in installed_apps:

            applications[app] = {}
            url_prefix = installed_apps[app]['PREFIX']
            del installed_apps[app]['PREFIX']

            if 'APP_VERSION' in installed_apps[app]:
                applications[app]['APP_VERSION'] = installed_apps[app]['APP_VERSION']
                del installed_apps[app]['APP_VERSION']

            for m in installed_apps[app]:

                mmod = installed_apps[app][m]

                base_pkg = hasattr(mmod, 'BASE') and mmod.BASE
                mm = {}
                mm['name'] = mmod.name

                a = doc_parser(mmod, url_prefix, base_pkg)
                mm.update(a)

                applications[app][mmod.name] = mm

    applist['applications'] = applications
    applist = json.dumps(applist)

    return applist


