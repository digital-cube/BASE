# coding= utf-8

class MissingApplicationPort(Exception):
    """Application port not configured or not in arguments"""
    pass


class MissingApiRui(Exception):
    """Missing uri from API decorator"""
    pass
