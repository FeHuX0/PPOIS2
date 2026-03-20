from abc import ABC, abstractmethod
from decimal import Decimal

from src.domain.bank_card import BankCard
from src.domain.card_limits import CardLimits
from src.domain.transaction import Transaction


class CardServiceInterface(ABC):
    """Abstraction for card operation use cases."""

    @property
    @abstractmethod
    def card(self) -> BankCard:
        """Return card aggregate."""

    @abstractmethod
    def withdraw(self, amount: Decimal, pin_code: str) -> Decimal:
        """Withdraw money from card balance."""

    @abstractmethod
    def deposit(self, amount: Decimal, pin_code: str) -> Decimal:
        """Deposit money to card balance."""

    @abstractmethod
    def pay(self, amount: Decimal, pin_code: str) -> Decimal:
        """Pay for goods or services."""

    @abstractmethod
    def get_balance(self, pin_code: str) -> Decimal:
        """Return current balance."""

    @abstractmethod
    def block_card(self, pin_code: str) -> None:
        """Block the card."""

    @abstractmethod
    def unblock_card(self, pin_code: str) -> None:
        """Unblock the card."""

    @abstractmethod
    def change_limits(
        self,
        withdrawal_limit: Decimal,
        payment_limit: Decimal,
        pin_code: str,
    ) -> CardLimits:
        """Set new limits."""

    @abstractmethod
    def get_transactions(self, pin_code: str) -> tuple[Transaction, ...]:
        """Return transaction history."""
