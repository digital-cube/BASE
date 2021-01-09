import datetime


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
