import re
import json
import base_config.settings as csettings
from base_common.importer import get_pkgs
from base_lookup.methods_mapping import method_map, method_map_rev
from base_lookup import http_methods
from base_config.settings import  __VERSION__


def fdoc_parser(doc):

    try:
        docl = doc.split('\n')
    except AttributeError:
        return 'Missing docstring'

    desc = ''
    params = {}
    _return = {}

    ps = ':(?P<grp>\w+)\s*(?P<prm>\w+)\s*:\s*(?P<desc>[^,]+)\s*,\s*(?P<tp>[^,]+)\s*,\s*(?P<req>\w+)$'
    rs = ':(?P<grp>\w+)\s*:\s*(?P<tp>\d+)\s*,?\s*(?P<desc>.*)?$'

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
                m = re.match(rs,l)
                ret = m.group('tp')
                if ret not in _return:
                    _return[ret] = {}
                mdesc = m.group('desc')
                _return[ret]['description'] = mdesc if mdesc else 'No content'
        else:
            if l:
                desc = l

    return {'description':desc, 'parameters': params, 'return': _return}


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


def doc_parser(doc):

    short_desc, long_desc = parse_module_desc(doc.__doc__)
    api = {
        'name': doc.name,
        'description': short_desc,
        'description_long': long_desc,
        'methods': {}}

    for v in method_map.values():
        if hasattr(doc,v):
            f = getattr(doc,v)
            http_method = http_methods.rev[method_map_rev[v]]
            api['methods'][http_method] = fdoc_parser(f.__doc__)

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
                mm['url'] = '/{}'.format(mmod.location) if base_pkg else '/{}/{}'.format(url_prefix, mmod.location)
                a = doc_parser(mmod)
                mm.update(a)

                applications[app][mmod.name] = mm

    applist['applications'] = applications
    applist = json.dumps(applist)

    return applist


