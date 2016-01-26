from base_lookup.http_methods import GET, PUT, DELETE, POST

method_map = {
    GET: 'do_get',
    PUT: 'do_put',
    DELETE: 'do_delete',
    POST: 'do_post',
}

method_map_rev = dict((y, x) for (x, y) in method_map.items())
