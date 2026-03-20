from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP

from src.core.enum import CardStatus
from src.domain.bank import Bank
from src.domain.card_limits import CardLimits
from src.domain.card_owner import CardOwner
from src.domain.transaction import Transaction


@dataclass(slots=True)
class BankCard:
    """Card aggregate with mutable balance, limits, and status."""

    card_number: str
    pin_code: str = field(repr=False)
    bank: Bank = field(repr=False)
    owner: CardOwner = field(repr=False)
    limits: CardLimits
    balance: Decimal = Decimal("0.00")
    status: CardStatus = CardStatus.ACTIVE
    _transactions: list[Transaction] = field(default_factory=list, repr=False)

    def __post_init__(self) -> None:
        self.card_number = self._normalize_card_number(self.card_number)
        self._validate_pin_code(self.pin_code)
        self.balance = self._normalize_balance(self.balance)

    @staticmethod
    def _normalize_card_number(card_number: str) -> str:
        normalized_number = card_number.replace(" ", "")
        if not normalized_number.isdigit() or len(normalized_number) != 16:
            raise ValueError("Card number must contain 16 digits.")
        return normalized_number

    @staticmethod
    def _validate_pin_code(pin_code: str) -> None:
        if not pin_code.isdigit() or len(pin_code) != 4:
            raise ValueError("PIN code must contain 4 digits.")

    @staticmethod
    def _normalize_balance(balance: Decimal) -> Decimal:
        normalized_balance = balance.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        if normalized_balance < Decimal("0"):
            raise ValueError("Initial balance cannot be negative.")
        return normalized_balance

    @property
    def masked_number(self) -> str:
        return f"**** **** **** {self.card_number[-4:]}"

    @property
    def transactions(self) -> tuple[Transaction, ...]:
        return tuple(self._transactions)

    def verify_pin(self, candidate_pin: str) -> bool:
        return self.pin_code == candidate_pin

    def add_transaction(self, transaction: Transaction) -> None:
        self._transactions.append(transaction)
