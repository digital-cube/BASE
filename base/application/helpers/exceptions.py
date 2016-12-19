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


class MissingApplicationConfiguration(Exception):
    """Application configuration part is missing."""
    pass


class UnknownDatabaseType(Exception):
    """Unknown database type provided"""
    pass


class SequencerTypeError(Exception):
    """Wrong Sequencer data type"""
    pass


class InvalidAPIHooksModule(Exception):
    """API Hooks module not configured or invalid"""
    pass


class UnknownSessionStorage(Exception):
    """Unknown session storage type"""
    pass


class ErrorSetSessionToken(Exception):
    """Error setting session token in configured storage"""
    pass


class MissingRolesLookup(Exception):
    """User roles lookup file is missiong or not configured"""
    pass


class PreLoginException(Exception):
    """Pre login process hook exception"""
    pass


class PostLoginException(Exception):
    """Post login process hook exception"""
    pass


class SaveHash2ParamsException(Exception):
    """Error save hash"""
    pass


class GetHash2ParamsException(Exception):
    """Error get hash data"""
    pass
