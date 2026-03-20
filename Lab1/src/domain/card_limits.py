from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP


@dataclass(slots=True)
class CardLimits:
    """Per-operation card limits."""

    withdrawal_limit: Decimal
    payment_limit: Decimal

    def __post_init__(self) -> None:
        self.withdrawal_limit = self._normalize_limit(
            value=self.withdrawal_limit,
            field_name="Withdrawal",
        )
        self.payment_limit = self._normalize_limit(
            value=self.payment_limit,
            field_name="Payment",
        )

    @staticmethod
    def _normalize_limit(value: Decimal, field_name: str) -> Decimal:
        normalized_value = value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        if normalized_value <= Decimal("0"):
            raise ValueError(f"{field_name} limit must be positive.")
        return normalized_value
