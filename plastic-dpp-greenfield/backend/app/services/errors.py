class DomainError(Exception):
    """Base class for domain errors mapped to HTTP responses in main.py."""


class NotFoundError(DomainError):
    pass


class InvalidTransitionError(DomainError):
    pass


class UnauthorizedRoleError(DomainError):
    pass


class InvalidTransactionError(DomainError):
    pass
