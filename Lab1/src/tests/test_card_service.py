from decimal import Decimal
import unittest

from src.core.enum import CardStatus, TransactionType
from src.core.exceptions import (
    CardBlockedError,
    InsufficientFundsError,
    InvalidAmountError,
    InvalidPinError,
    LimitExceededError,
)
from src.domain.bank import Bank
from src.domain.bank_card import BankCard
from src.domain.card_limits import CardLimits
from src.domain.card_owner import CardOwner
from src.services.card_service import CardService


class CardServiceTestCase(unittest.TestCase):
    def setUp(self) -> None:
        card = BankCard(
            card_number="1234567812345678",
            pin_code="1234",
            bank=Bank(name="Test Bank", bic="TESTBIC1"),
            owner=CardOwner(full_name="Test User", owner_id="U-1"),
            limits=CardLimits(
                withdrawal_limit=Decimal("500.00"),
                payment_limit=Decimal("700.00"),
            ),
            balance=Decimal("1000.00"),
        )
        self.service: CardService = CardService(card=card)

    def test_deposit_increases_balance_and_creates_transaction(self) -> None:
        balance = self.service.deposit(amount=Decimal("100.00"), pin_code="1234")

        self.assertEqual(balance, Decimal("1100.00"))
        self.assertEqual(
            self.service.card.transactions[-1].transaction_type,
            TransactionType.DEPOSIT,
        )

    def test_withdraw_fails_when_limit_exceeded(self) -> None:
        with self.assertRaises(LimitExceededError):
            self.service.withdraw(amount=Decimal("600.00"), pin_code="1234")

    def test_payment_fails_when_insufficient_funds(self) -> None:
        self.service.withdraw(amount=Decimal("400.00"), pin_code="1234")
        with self.assertRaises(InsufficientFundsError):
            self.service.pay(amount=Decimal("650.00"), pin_code="1234")

    def test_invalid_pin_raises_error(self) -> None:
        with self.assertRaises(InvalidPinError):
            self.service.get_balance(pin_code="0000")

    def test_block_and_unblock_card(self) -> None:
        self.service.block_card(pin_code="1234")
        self.assertEqual(self.service.card.status, CardStatus.BLOCKED)

        with self.assertRaises(CardBlockedError):
            self.service.get_balance(pin_code="1234")

        self.service.unblock_card(pin_code="1234")
        self.assertEqual(self.service.card.status, CardStatus.ACTIVE)

    def test_change_limits_updates_card_limits(self) -> None:
        limits = self.service.change_limits(
            withdrawal_limit=Decimal("900.00"),
            payment_limit=Decimal("1200.00"),
            pin_code="1234",
        )

        self.assertEqual(limits.withdrawal_limit, Decimal("900.00"))
        self.assertEqual(limits.payment_limit, Decimal("1200.00"))

    def test_negative_amount_raises_error(self) -> None:
        with self.assertRaises(InvalidAmountError):
            self.service.deposit(amount=Decimal("-10.00"), pin_code="1234")

    def test_state_change_hook_called_after_successful_operation(self) -> None:
        calls: list[Decimal] = []
        card = BankCard(
            card_number="1234567812345678",
            pin_code="1234",
            bank=Bank(name="Test Bank", bic="TESTBIC1"),
            owner=CardOwner(full_name="Test User", owner_id="U-1"),
            limits=CardLimits(
                withdrawal_limit=Decimal("500.00"),
                payment_limit=Decimal("700.00"),
            ),
            balance=Decimal("1000.00"),
        )
        service = CardService(card=card, on_state_change=lambda state: calls.append(state.balance))

        service.deposit(amount=Decimal("10.00"), pin_code="1234")

        self.assertEqual(calls, [Decimal("1010.00")])


if __name__ == "__main__":
    unittest.main()
