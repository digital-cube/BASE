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


class MissingDatabaseConfigurationForPort(Exception):
    """Application port database configuration missing"""
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
    """User roles lookup file is missing or not configured"""
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


class PreLogoutException(Exception):
    """Pre logout process hook exception"""
    pass


class PostLogoutException(Exception):
    """Post logout process hook exception"""
    pass


class CheckUserError(Exception):
    """Check user error exception"""
    pass


class PreCheckUserError(Exception):
    """Pre check user process error exception"""
    pass


class PostCheckUserError(Exception):
    """Post check user process error exception"""
    pass


class MailQueueError(Exception):
    """Create mail queue error exception"""
    pass


class InvalidRequestParameter(Exception):
    """Invalid request parameter"""
    pass


class MissingRequestArgument(Exception):
    """Request argument is missing"""
    pass


class InvalidApplicationConfiguration(Exception):
    """Application configuration is invalid"""
    pass


class DatabaseIsNotConfigured(Exception):
    """Application has not database configured"""
    pass


class PreApplicationProcessConfigurationError(Exception):
    """Pre application processes not configured properly"""
    pass


class PostApplicationProcessConfigurationError(Exception):
    """Post application processes not configured properly"""
    pass


class MissingModelsConfig(Exception):
    """Database models json is missing"""
    pass


class MissingLanguagesLookup(Exception):
    """Languages lookup file is missing or not configured"""
    pass


class ErrorLanguagesLookup(Exception):
    """Languages lookup file is badly configured"""
    pass


class ErrorLanguageCodeID(Exception):
    """Language code id has to be two lowercase characters"""
    pass


class ReadOnlyAllowedOnlyForGET(Exception):
    """readonly allowed only for get"""
    pass


class ReadOnlyCanWrapOnlyFunction(Exception):
    """only functions can be wrapped with readonly"""
    pass


class WrongAuthenticationLevel(Exception):
    """authentication level provided not known"""
    pass


class InvalidRedirectURL(Exception):
    """invalid redirect URL provided"""
    pass
