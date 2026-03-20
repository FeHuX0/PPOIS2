from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import Decimal, ROUND_HALF_UP
from uuid import uuid4

from src.core.enum import TransactionType


@dataclass(frozen=True, slots=True)
class Transaction:
    """Immutable transaction log record."""

    transaction_type: TransactionType
    amount: Decimal
    balance_after: Decimal
    description: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    transaction_id: str = field(default_factory=lambda: uuid4().hex)

    def __post_init__(self) -> None:
        normalized_amount = self._normalize_money(self.amount)
        normalized_balance = self._normalize_money(self.balance_after)
        if normalized_amount < Decimal("0"):
            raise ValueError("Transaction amount cannot be negative.")
        if not self.description.strip():
            raise ValueError("Transaction description cannot be empty.")
        object.__setattr__(self, "amount", normalized_amount)
        object.__setattr__(self, "balance_after", normalized_balance)

    @staticmethod
    def _normalize_money(value: Decimal) -> Decimal:
        return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
