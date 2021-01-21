import datetime


def get_request_ip(request_handler):
    """
    Get the IP address from request handler object
    :param request_handler: request handler object
    :return: IP address string
    """
    _proxy_ip = request_handler.request.headers.get('X-Forwarded-For')
    _ip = _proxy_ip or request_handler.request.remote_ip
    return _ip


def get_pages_counts(total_number_of_elements, limit, offset):
    """
    Calculate current page and total pages
    :param total_number_of_elements: int - number of elements for calculating page numbers
    :param limit: int - limit of elements to be shown on a page
    :param offset: int - offset for elements
    :return:
        total_pages - int - number of total pages for given number of elements
        current_page - int - number of a current page for given number of elements and a limit
    """
    _total_pages = (total_number_of_elements // limit) or 1
    if _total_pages * limit < total_number_of_elements:
        _total_pages += 1
    _current_page = offset // limit + 1

    return _total_pages, _current_page


def filter_only_allowed_keys(allowed: list, source: list):
    source = set(source if source else [])

    return [k for k in allowed if k in source]


def missing_keys(source, expected_keys: list):
    if not source:
        return expected_keys

    missing = []
    for key in expected_keys:
        if key not in source:
            missing.append(key)

    return missing


def fdate(s):
    if type(s) == datetime.datetime:
        return s.date()
    if type(s) == datetime.date:
        return s
    return 'N/A'
