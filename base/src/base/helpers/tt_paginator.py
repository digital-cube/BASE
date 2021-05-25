"""
Paginate helper for Tortoase select queries
"""

import inspect


async def tt_paginate(query, base_uri, page, per_page, query_params=[]):
    """
    Paginate
    """

    query_params = '?'+'&'.join(query_params) if query_params else ''


    if page < 1:
        raise NameError('page should be greater than zero')
    if per_page < 1:
        raise NameError('per page should be greater than zero')

    limit = per_page
    offset = (page - 1) * per_page

    total_items = await query.count()

    total_pages = total_items // per_page + \
                  (1 if total_items % per_page else 0)

    query = query.offset(offset).limit(limit)

    base_uri = base_uri + query_params
    base_uri = base_uri + ("&" if '?' in base_uri else '?')

    previous_uri, next_uri = None, None
    if page < total_pages:
        next_uri = f'{base_uri}page={page + 1}&per_page={per_page}'

    if page > 1:
        previous_uri = f'{base_uri}page={page - 1}&per_page={per_page}'

    summary = {
        'total_pages': total_pages,
        'total_items': total_items,
        'page': page,
        'per_page': per_page,
        'next': next_uri,
        'previous': previous_uri,
    }
    return query, summary
