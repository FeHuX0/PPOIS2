class CardError(Exception):
    """Base exception for card operations."""


class InvalidPinError(CardError):
    """Raised when an incorrect PIN code is provided."""


class CardBlockedError(CardError):
    """Raised when an operation is attempted on a blocked card."""


class CardAlreadyBlockedError(CardError):
    """Raised when trying to block an already blocked card."""


class CardAlreadyActiveError(CardError):
    """Raised when trying to unblock an already active card."""


class InsufficientFundsError(CardError):
    """Raised when card balance is not enough for an operation."""


class LimitExceededError(CardError):
    """Raised when operation amount exceeds card limits."""


class InvalidAmountError(CardError):
    """Raised when amount is invalid."""
