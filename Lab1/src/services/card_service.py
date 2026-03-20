from collections.abc import Callable
from decimal import Decimal, ROUND_HALF_UP
from typing import Final

from src.core.enum import CardStatus, TransactionType
from src.core.exceptions import (
    CardAlreadyActiveError,
    CardAlreadyBlockedError,
    CardBlockedError,
    InsufficientFundsError,
    InvalidAmountError,
    InvalidPinError,
    LimitExceededError,
)
from src.domain.bank_card import BankCard
from src.domain.card_limits import CardLimits
from src.domain.transaction import Transaction
from src.services.interfaces import CardServiceInterface

MONEY_PRECISION: Final[Decimal] = Decimal("0.01")
StateChangeHook = Callable[[BankCard], None]


def _normalize_money(value: Decimal) -> Decimal:
    return value.quantize(MONEY_PRECISION, rounding=ROUND_HALF_UP)


class CardService(CardServiceInterface):
    """Application service that orchestrates card operations."""

    def __init__(
        self,
        card: BankCard,
        on_state_change: StateChangeHook | None = None,
    ) -> None:
        self._card = card
        self._on_state_change = on_state_change

    @property
    def card(self) -> BankCard:
        return self._card

    def withdraw(self, amount: Decimal, pin_code: str) -> Decimal:
        normalized_amount = self._prepare_financial_operation(amount, pin_code)
        if normalized_amount > self._card.limits.withdrawal_limit:
            raise LimitExceededError("Withdrawal amount exceeds withdrawal limit.")
        if normalized_amount > self._card.balance:
            raise InsufficientFundsError("Insufficient funds for withdrawal.")
        self._card.balance = _normalize_money(self._card.balance - normalized_amount)
        self._log_transaction(
            transaction_type=TransactionType.WITHDRAWAL,
            amount=normalized_amount,
            description="Cash withdrawal",
        )
        return self._card.balance

    def deposit(self, amount: Decimal, pin_code: str) -> Decimal:
        normalized_amount = self._prepare_financial_operation(amount, pin_code)
        self._card.balance = _normalize_money(self._card.balance + normalized_amount)
        self._log_transaction(
            transaction_type=TransactionType.DEPOSIT,
            amount=normalized_amount,
            description="Cash deposit",
        )
        return self._card.balance

    def pay(self, amount: Decimal, pin_code: str) -> Decimal:
        normalized_amount = self._prepare_financial_operation(amount, pin_code)
        if normalized_amount > self._card.limits.payment_limit:
            raise LimitExceededError("Payment amount exceeds payment limit.")
        if normalized_amount > self._card.balance:
            raise InsufficientFundsError("Insufficient funds for payment.")
        self._card.balance = _normalize_money(self._card.balance - normalized_amount)
        self._log_transaction(
            transaction_type=TransactionType.PAYMENT,
            amount=normalized_amount,
            description="Payment for goods/services",
        )
        return self._card.balance

    def get_balance(self, pin_code: str) -> Decimal:
        self._authorize(pin_code)
        self._ensure_active()
        self._log_transaction(
            transaction_type=TransactionType.BALANCE_CHECK,
            amount=Decimal("0.00"),
            description="Balance check",
        )
        return self._card.balance

    def block_card(self, pin_code: str) -> None:
        self._authorize(pin_code)
        if self._card.status == CardStatus.BLOCKED:
            raise CardAlreadyBlockedError("Card is already blocked.")
        self._card.status = CardStatus.BLOCKED
        self._log_transaction(
            transaction_type=TransactionType.BLOCK,
            amount=Decimal("0.00"),
            description="Card blocked",
        )

    def unblock_card(self, pin_code: str) -> None:
        self._authorize(pin_code)
        if self._card.status == CardStatus.ACTIVE:
            raise CardAlreadyActiveError("Card is already active.")
        self._card.status = CardStatus.ACTIVE
        self._log_transaction(
            transaction_type=TransactionType.UNBLOCK,
            amount=Decimal("0.00"),
            description="Card unblocked",
        )

    def change_limits(
        self,
        withdrawal_limit: Decimal,
        payment_limit: Decimal,
        pin_code: str,
    ) -> CardLimits:
        self._authorize(pin_code)
        self._ensure_active()
        normalized_withdrawal = _normalize_money(withdrawal_limit)
        normalized_payment = _normalize_money(payment_limit)
        if normalized_withdrawal <= Decimal("0") or normalized_payment <= Decimal("0"):
            raise InvalidAmountError("New limits must be positive values.")
        self._card.limits = CardLimits(
            withdrawal_limit=normalized_withdrawal,
            payment_limit=normalized_payment,
        )
        self._log_transaction(
            transaction_type=TransactionType.LIMIT_CHANGE,
            amount=Decimal("0.00"),
            description=(
                "Limits changed: "
                f"withdrawal={normalized_withdrawal}, payment={normalized_payment}"
            ),
        )
        return self._card.limits

    def get_transactions(self, pin_code: str) -> tuple[Transaction, ...]:
        self._authorize(pin_code)
        return self._card.transactions

    def _prepare_financial_operation(
        self,
        amount: Decimal,
        pin_code: str,
    ) -> Decimal:
        self._authorize(pin_code)
        self._ensure_active()
        normalized_amount = _normalize_money(amount)
        if normalized_amount <= Decimal("0"):
            raise InvalidAmountError("Amount must be greater than zero.")
        return normalized_amount

    def _authorize(self, pin_code: str) -> None:
        if not self._card.verify_pin(pin_code):
            raise InvalidPinError("Invalid PIN code.")

    def _ensure_active(self) -> None:
        if self._card.status == CardStatus.BLOCKED:
            raise CardBlockedError("Card is blocked.")

    def _log_transaction(
        self,
        transaction_type: TransactionType,
        amount: Decimal,
        description: str,
    ) -> None:
        self._card.add_transaction(
            Transaction(
                transaction_type=transaction_type,
                amount=_normalize_money(amount),
                balance_after=self._card.balance,
                description=description,
            )
        )
        self._notify_state_change()

    def _notify_state_change(self) -> None:
        if self._on_state_change is not None:
            self._on_state_change(self._card)
