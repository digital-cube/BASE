'''
Paginate helper for Tortoase select queries
'''

import inspect


async def tt_paginate(query, base_uri, page, per_page, query_params=[], count_by_iteration=False, fast_count=False, count_url: str = None,
                      force_fast_count_result=None):
    '''
    Paginate
    '''

    if fast_count and not count_by_iteration:
        raise NameError("Invalid params combination fast_count must be followed with count by_iteration")

    query_params = '?' + '&'.join(query_params) if query_params else ''

    if page < 1:
        raise NameError('page should be greater than zero')
    if per_page < 1:
        raise NameError('per page should be greater than zero')

    limit = per_page
    offset = (page - 1) * per_page

    calc_pages = False
    of_xxx = False

    if not count_by_iteration:
        total_items = await query.count()
        calc_pages = True
    else:

        if force_fast_count_result:
            total_items = force_fast_count_result
            calc_pages = True

        else:
            total_items = 0
            for _ in await query.all():
                total_items += 1

                if total_items > 100 and fast_count:
                    of_xxx = True
                    break

    query = query.offset(offset).limit(limit)

    if calc_pages:
        total_pages = total_items // per_page + \
                      (1 if total_items % per_page else 0)

        base_uri = base_uri + query_params
        base_uri = base_uri + ("&" if '?' in base_uri else '?')

        previous_uri, next_uri = None, None
        if page < total_pages:
            next_uri = f'{base_uri}page={page + 1}&per_page={per_page}'

        if page > 1:
            previous_uri = f'{base_uri}page={page - 1}&per_page={per_page}'

    else:
        total_pages = None
        base_uri = base_uri + query_params
        base_uri = base_uri + ("&" if '?' in base_uri else '?')
        previous_uri, next_uri = None, None

    summary = {
        'total_pages': total_pages,
        'total_items': total_items if not of_xxx else 'OF_HUNDREDS',
        'page': page,
        'per_page': per_page,
        'next': next_uri,
        'previous': previous_uri,
    }

    if fast_count:
        summary.update({
            'fast_count': fast_count,
            'count_url': count_url if of_xxx else None,
            # 'force_fast_count_result': force_fast_count_result
        }
        )

    return query, summary
