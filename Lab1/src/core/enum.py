from enum import Enum


class CardStatus(str, Enum):
    """Current state of a bank card."""

    ACTIVE = "active"
    BLOCKED = "blocked"


class TransactionType(str, Enum):
    """Supported transaction types."""

    WITHDRAWAL = "withdrawal"
    DEPOSIT = "deposit"
    PAYMENT = "payment"
    BALANCE_CHECK = "balance_check"
    BLOCK = "block"
    UNBLOCK = "unblock"
    LIMIT_CHANGE = "limit_change"


class CliState(str, Enum):
    """Current state of CLI loop."""

    RUNNING = "running"
    STOPPED = "stopped"


class CliCommand(str, Enum):
    """Supported CLI commands."""

    BALANCE_CHECK = "1"
    WITHDRAW = "2"
    DEPOSIT = "3"
    PAYMENT = "4"
    BLOCK = "5"
    UNBLOCK = "6"
    CHANGE_LIMITS = "7"
    HISTORY = "8"
    EXIT = "0"
