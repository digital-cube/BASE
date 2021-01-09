'''
Paginate helper for SqlAlchemy select queries
'''


def paginate(query, base_uri, page, per_page):
    '''
    Paginate
    '''

    if page < 1:
        raise NameError('page should be greater than zero')
    if per_page < 1:
        raise NameError('per page should be greater than zero')

    limit = per_page
    offset = (page - 1) * per_page

    total_items = query.count()
    total_pages = total_items // per_page + \
                  (1 if total_items % per_page else 0)

    query = query.offset(offset).limit(limit)

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


def paginate_groups(query, base_uri, page, per_page):
    '''
    Paginate groups
    '''
    limit = per_page
    offset = (page - 1) * per_page

    total_items = query.count()
    total_pages = total_items // per_page + \
                  (1 if total_items % per_page else 0)

    query = query.offset(offset).limit(limit)

    base_uri = base_uri + ("&" if '?' in base_uri else '?')

    if page == 1:
        next_uri = f'{base_uri}products_page={page + 1}&products_per_page={per_page}'
        previous_uri = None
    elif page == total_pages:
        next_uri = None
        previous_uri = f'{base_uri}products_page={page - 1}&products_per_page={per_page}'
    else:
        next_uri = f'{base_uri}products_page={page + 1}&products_per_page={per_page}'
        previous_uri = f'{base_uri}products_page={page - 1}&products_per_page={per_page}'

    summary = {
        'total_pages': total_pages,
        'total_items': total_items,
        'page': page,
        'per_page': per_page,
        'next': next_uri,
        'previous': previous_uri,
    }
    return query, summary
