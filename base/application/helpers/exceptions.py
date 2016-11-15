# coding= utf-8


class MissingApplicationPort(Exception):
    """Application port not configured or not in arguments"""
    pass


class MissingApiRui(Exception):
    """Missing uri from API decorator"""
    pass


class ToManyAttemptsException(Exception):
    """Number of attempts excited. For db insertions and others."""
    pass


class MissingApplicationConfigurationException(Exception):
    """Application configuration part is missing."""
    pass


class UnknownDatabaseType(Exception):
    """Unknown database type provided"""
    pass
